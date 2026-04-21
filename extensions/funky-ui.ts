import { spawnSync } from "node:child_process";
import { basename, relative, sep } from "node:path";
import type { Model } from "@mariozechner/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@mariozechner/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@mariozechner/pi-tui";
import { ANIMATIONS } from "./funky-ui/animations.js";

type WorkingIndicatorOptions = {
	frames?: string[];
	intervalMs?: number;
};

type FooterState = {
	model: Model<any> | null;
	ctx: ExtensionContext | null;
	starshipLeft: string | null;
};

const state: FooterState = {
	model: null,
	ctx: null,
	starshipLeft: null,
};

let cachedGitRoot: { cwd: string; root: string | null } = { cwd: "", root: null };
let requestFooterRender: (() => void) | null = null;

function normalizeSlashes(value: string): string {
	return value.split(sep).join("/");
}

function getGitRoot(cwd: string): string | null {
	if (cachedGitRoot.cwd === cwd) {
		return cachedGitRoot.root;
	}

	const result = spawnSync("git", ["-C", cwd, "rev-parse", "--show-toplevel"], {
		encoding: "utf8",
		stdio: ["ignore", "pipe", "ignore"],
	});

	const root = result.status === 0 ? result.stdout.trim() || null : null;
	cachedGitRoot = { cwd, root };
	return root;
}

function formatOutsideRepoPath(cwd: string): string {
	const home = process.env.HOME || process.env.USERPROFILE;
	if (home && (cwd === home || cwd.startsWith(`${home}${sep}`))) {
		const suffix = cwd.slice(home.length);
		return suffix ? `~${normalizeSlashes(suffix)}` : "~";
	}

	return normalizeSlashes(cwd);
}

function formatDisplayPath(cwd: string): string {
	const gitRoot = getGitRoot(cwd);
	if (!gitRoot) {
		return formatOutsideRepoPath(cwd);
	}

	const repoName = basename(gitRoot);
	const repoRelative = normalizeSlashes(relative(gitRoot, cwd));
	return repoRelative ? `${repoName}/${repoRelative}` : repoName;
}

function updateState(ctx: ExtensionContext): void {
	state.ctx = ctx;
	state.model = ctx.model ?? null;
}

function stripShellPromptEscapes(value: string): string {
	return value.replace(/%\{/g, "").replace(/%\}/g, "").replace(/\\\[/g, "").replace(/\\\]/g, "");
}

function resolveStarshipPromptLine(output: string): string | null {
	const lines = output
		.replace(/\r/g, "")
		.split("\n")
		.map((line) => stripShellPromptEscapes(line).trimEnd());

	for (const line of lines) {
		if (line.length > 0) {
			return line;
		}
	}

	return null;
}

function readStarshipLeftSegment(cwd: string): string | null {
	const env = { ...process.env };
	delete env.STARSHIP_SHELL;

	const result = spawnSync("starship", ["prompt", "-p", cwd, "-k", "viins", "-w", "512"], {
		encoding: "utf8",
		stdio: ["ignore", "pipe", "ignore"],
		env,
	});

	if (result.status !== 0) {
		return null;
	}

	return resolveStarshipPromptLine(result.stdout);
}

function refreshStarshipLeft(ctx: ExtensionContext): void {
	const cwd = ctx.sessionManager.getCwd() ?? process.cwd();
	state.starshipLeft = readStarshipLeftSegment(cwd);
}

function formatModelSegment(theme: any): string {
	const modelLabel = state.model?.name || state.model?.id || "no-model";
	return theme.fg("muted", modelLabel);
}

function formatContextSegment(theme: any, contextPercent: number | null): string | null {
	if (contextPercent === null) {
		return null;
	}

	const roundedPercent = Math.round(contextPercent);
	return theme.fg("muted", `${roundedPercent}%`);
}

function formatLocation(branch: string | null): string {
	const cwd = state.ctx?.sessionManager.getCwd() ?? process.cwd();
	const displayPath = formatDisplayPath(cwd);
	return branch ? `${displayPath} on ${branch}` : displayPath;
}

function buildWorkingIndicator(theme: ExtensionContext["ui"]["theme"]): WorkingIndicatorOptions {
	const lastIndex = ANIMATIONS.pulse.frames.length - 1;
	return {
		frames: ANIMATIONS.pulse.frames.map((frame, index) => {
			const color = index === 0 || index === lastIndex
				? "dim"
				: index === 1 || index === lastIndex - 1
					? "muted"
					: "accent";
			return theme.fg(color, frame);
		}),
		intervalMs: ANIMATIONS.pulse.interval,
	};
}

function installWorkingIndicator(ctx: ExtensionContext): void {
	const ui = ctx.ui as ExtensionContext["ui"] & {
		setWorkingIndicator?: (options?: WorkingIndicatorOptions) => void;
	};

	ui.setWorkingIndicator?.(buildWorkingIndicator(ctx.ui.theme));
}

function formatRightSegment(theme: any, contextPercent: number | null): string {
	const separator = theme.fg("muted", " | ");
	const segments = [formatModelSegment(theme), formatContextSegment(theme, contextPercent)].filter(Boolean) as string[];
	return segments.join(separator);
}

function formatFooterLine(left: string, right: string, width: number): string {
	if (!right) {
		return truncateToWidth(left, width, width > 3 ? "..." : "");
	}

	const rightWidth = visibleWidth(right);
	if (rightWidth >= width) {
		return truncateToWidth(right, width, width > 3 ? "..." : "");
	}

	const leftWidth = visibleWidth(left);
	if (leftWidth + 1 + rightWidth <= width) {
		return `${left}${" ".repeat(width - leftWidth - rightWidth)}${right}`;
	}

	const leftWidthBudget = Math.max(1, width - rightWidth - 1);
	const truncatedLeft = truncateToWidth(left, leftWidthBudget, leftWidthBudget > 3 ? "..." : "");
	const paddingWidth = Math.max(1, width - visibleWidth(truncatedLeft) - rightWidth);
	return `${truncatedLeft}${" ".repeat(paddingWidth)}${right}`;
}

export default function (pi: ExtensionAPI) {
	pi.on("session_start", async (_event, ctx) => {
		updateState(ctx);
		refreshStarshipLeft(ctx);
		installWorkingIndicator(ctx);

		ctx.ui.setFooter((tui, theme, footerData) => {
			requestFooterRender = () => tui.requestRender();
			const unsubscribeBranch = footerData.onBranchChange(() => {
				if (state.ctx) {
					refreshStarshipLeft(state.ctx);
				}
				tui.requestRender();
			});
			return {
				dispose() {
					requestFooterRender = null;
					unsubscribeBranch();
				},
				invalidate() {},
				render(width: number): string[] {
					const contextPercent = state.ctx?.getContextUsage()?.percent ?? null;
					const leftSegment =
						state.starshipLeft ??
						theme.fg("muted", formatLocation(footerData.getGitBranch()));
					const rightSegment = formatRightSegment(theme, contextPercent);
					return [formatFooterLine(leftSegment, rightSegment, width)];
				},
			};
		});
	});

	pi.on("model_select", async (_event, ctx) => {
		updateState(ctx);
		requestFooterRender?.();
	});

	pi.on("session_tree", async (_event, ctx) => {
		updateState(ctx);
		refreshStarshipLeft(ctx);
		requestFooterRender?.();
	});

	pi.on("turn_end", async (_event, ctx) => {
		updateState(ctx);
		refreshStarshipLeft(ctx);
		requestFooterRender?.();
	});

	pi.on("agent_end", async (_event, ctx) => {
		updateState(ctx);
		refreshStarshipLeft(ctx);
		requestFooterRender?.();
	});
}
