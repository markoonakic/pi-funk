import { spawnSync } from "node:child_process";
import { basename, relative, sep } from "node:path";
import { supportsXhigh, type Model, type ThinkingLevel } from "@mariozechner/pi-ai";
import type { ExtensionAPI, ExtensionContext } from "@mariozechner/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@mariozechner/pi-tui";

type FooterState = {
	model: Model<any> | null;
	ctx: ExtensionContext | null;
};

const state: FooterState = {
	model: null,
	ctx: null,
};

let cachedGitRoot: { cwd: string; root: string | null } = { cwd: "", root: null };
let requestFooterRender: (() => void) | null = null;
const THINKING_LEVELS: ThinkingLevel[] = ["off", "minimal", "low", "medium", "high"];
const THINKING_LEVELS_WITH_XHIGH: ThinkingLevel[] = ["off", "minimal", "low", "medium", "high", "xhigh"];

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

export function getNextThinkingLevel(model: Model<any> | null, currentLevel: string): ThinkingLevel | undefined {
	if (!model?.reasoning) {
		return undefined;
	}

	const levels = supportsXhigh(model) ? THINKING_LEVELS_WITH_XHIGH : THINKING_LEVELS;
	const currentIndex = levels.indexOf(currentLevel as ThinkingLevel);
	const nextIndex = currentIndex >= 0 ? (currentIndex + 1) % levels.length : 0;
	return levels[nextIndex];
}

function getFooterThinkingToken(level: string): string {
	switch (level) {
		case "low":
			return "mdLink";
		case "medium":
			return "mdCode";
		case "high":
			return "accent";
		case "xhigh":
			return "error";
		case "off":
		case "minimal":
		default:
			return "muted";
	}
}

function formatModelSegment(theme: any, thinkingLevel: string): string {
	const modelLabel = state.model?.name || state.model?.id || "no-model";
	if (!state.model?.reasoning || thinkingLevel === "off") {
		return theme.fg("accent", modelLabel);
	}

	return theme.fg("accent", modelLabel) + theme.fg(getFooterThinkingToken(thinkingLevel), ` ${thinkingLevel}`);
}

function formatContextSegment(theme: any, contextPercent: number | null): string | null {
	if (contextPercent === null) {
		return null;
	}

	const roundedPercent = Math.round(contextPercent);
	if (roundedPercent >= 90) {
		return theme.fg("error", `${roundedPercent}%`);
	}
	if (roundedPercent >= 70) {
		return theme.fg("warning", `${roundedPercent}%`);
	}
	return theme.fg("muted", `${roundedPercent}%`);
}

function formatLocation(branch: string | null): string {
	const cwd = state.ctx?.sessionManager.getCwd() ?? process.cwd();
	const displayPath = formatDisplayPath(cwd);
	return branch ? `${displayPath} on ${branch}` : displayPath;
}

export default function (pi: ExtensionAPI) {
	pi.registerShortcut("shift+tab", {
		description: "Cycle thinking level without transient status text",
		handler: async (ctx) => {
			updateState(ctx);
			const nextLevel = getNextThinkingLevel(state.model, pi.getThinkingLevel());
			if (!nextLevel) {
				return;
			}

			pi.setThinkingLevel(nextLevel);
			requestFooterRender?.();
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		updateState(ctx);

		ctx.ui.setFooter((tui, theme, footerData) => {
			requestFooterRender = () => tui.requestRender();
			const unsubscribeBranch = footerData.onBranchChange(() => tui.requestRender());
			return {
				dispose() {
					requestFooterRender = null;
					unsubscribeBranch();
				},
				invalidate() {},
				render(width: number): string[] {
					const thinkingLevel = pi.getThinkingLevel();
					const contextPercent = state.ctx?.getContextUsage()?.percent ?? null;
					const separator = theme.fg("dim", " | ");
					const staticSegments = [formatModelSegment(theme, thinkingLevel), formatContextSegment(theme, contextPercent)].filter(
						Boolean,
					) as string[];
					const reservedWidth =
						staticSegments.reduce((total, segment) => total + visibleWidth(segment), 0) +
						visibleWidth(separator) * staticSegments.length;
					const locationWidth = Math.max(1, width - reservedWidth);
					const locationSegment = theme.fg(
						"muted",
						truncateToWidth(formatLocation(footerData.getGitBranch()), locationWidth, locationWidth > 3 ? "..." : ""),
					);

					const line =
						staticSegments.length > 0
							? `${locationSegment}${separator}${staticSegments.join(separator)}`
							: locationSegment;

					return [truncateToWidth(line, width, width > 3 ? "..." : "")];
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
		requestFooterRender?.();
	});

	pi.on("turn_end", async (_event, ctx) => {
		updateState(ctx);
		requestFooterRender?.();
	});
}
