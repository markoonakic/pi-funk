import { spawnSync } from "node:child_process";
import { basename, relative, sep } from "node:path";
import type { Model } from "@mariozechner/pi-ai";
import { VERSION, type ExtensionAPI, type ExtensionContext } from "@mariozechner/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@mariozechner/pi-tui";
import { ANIMATIONS } from "./funky-ui/animations.js";
import { composeHeaderLines, renderAsciiLogoLines } from "./funky-ui/logo.js";

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

const SESSION_NAME_MAX_WIDTH = 32;
const SESSION_NAME_MIN_WIDTH = 8;
const SESSION_NAME_WIDTH_RATIO = 0.25;

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

function sanitizeFooterSegment(value: string): string {
	return value
		.replace(/\x1b\[[0-9;]*m/g, "")
		.replace(/[\r\n\t]/g, " ")
		.replace(/[\x00-\x1f\x7f]/g, "")
		.replace(/ +/g, " ")
		.trim();
}

function getSessionName(): string | null {
	const name = state.ctx?.sessionManager.getSessionName();
	if (!name) {
		return null;
	}

	const sanitized = sanitizeFooterSegment(name);
	return sanitized.length > 0 ? sanitized : null;
}

function getSessionNameWidthBudget(
	width: number,
	reservedRightWidth: number,
	separatorWidth: number,
	sessionNameWidth: number,
): number {
	const maxRightWidth = Math.max(0, width - 1);
	const availableWidth = maxRightWidth - reservedRightWidth - separatorWidth;
	if (availableWidth <= 0) {
		return 0;
	}

	const preferredWidth = Math.min(
		SESSION_NAME_MAX_WIDTH,
		Math.max(SESSION_NAME_MIN_WIDTH, Math.floor(width * SESSION_NAME_WIDTH_RATIO)),
	);
	const widthBudget = Math.min(availableWidth, preferredWidth);

	if (sessionNameWidth <= widthBudget) {
		return sessionNameWidth;
	}

	return widthBudget >= SESSION_NAME_MIN_WIDTH ? widthBudget : 0;
}

function formatSessionNameSegment(theme: any, name: string, maxWidth: number): string | null {
	if (maxWidth <= 0) {
		return null;
	}

	const truncatedName = truncateToWidth(name, maxWidth, maxWidth > 3 ? "..." : "");
	return truncatedName ? theme.fg("muted", truncatedName) : null;
}

function formatLocation(branch: string | null): string {
	const cwd = state.ctx?.sessionManager.getCwd() ?? process.cwd();
	const displayPath = formatDisplayPath(cwd);
	return branch ? `${displayPath} on ${branch}` : displayPath;
}

function installHeader(ctx: ExtensionContext): void {
	ctx.ui.setHeader((tui, theme) => {
		return {
			dispose() {},
			invalidate() {},
			render(width: number): string[] {
				const logoLines = renderAsciiLogoLines(theme, { bold: true });
				const versionLine = theme.fg("text", "pi ") + theme.fg("dim", `v${VERSION}`);
				return [
					...composeHeaderLines(logoLines, versionLine, width),
					"",
				];
			},
		};
	});
}

function buildWorkingIndicator(theme: ExtensionContext["ui"]["theme"]): WorkingIndicatorOptions {
	return {
		frames: ANIMATIONS.pulse.frames.map((frame) => theme.fg("accent", frame)),
		intervalMs: ANIMATIONS.pulse.interval,
	};
}

function installWorkingIndicator(ctx: ExtensionContext): void {
	const ui = ctx.ui as ExtensionContext["ui"] & {
		setWorkingIndicator?: (options?: WorkingIndicatorOptions) => void;
	};

	ui.setWorkingIndicator?.(buildWorkingIndicator(ctx.ui.theme));
}

function formatRightSegment(theme: any, contextPercent: number | null, width: number): string {
	const separator = theme.fg("muted", " | ");
	const coreSegments = [
		formatModelSegment(theme),
		formatContextSegment(theme, contextPercent),
	].filter(Boolean) as string[];
	const coreRightSegment = coreSegments.join(separator);
	const sessionName = getSessionName();
	const sessionNameWidth = sessionName
		? getSessionNameWidthBudget(
			width,
			visibleWidth(coreRightSegment),
			visibleWidth(separator),
			visibleWidth(sessionName),
		)
		: 0;
	const sessionNameSegment = sessionName
		? formatSessionNameSegment(theme, sessionName, sessionNameWidth)
		: null;
	const segments = [sessionNameSegment, ...coreSegments].filter(Boolean) as string[];
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
		installHeader(ctx);
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
					const rightSegment = formatRightSegment(theme, contextPercent, width);
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
