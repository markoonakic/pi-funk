import { readFileSync } from "node:fs";

type ThemeLike = {
	fg(color: string, text: string): string;
	bold?(text: string): string;
};

const ASCII_PATH = new URL("./ascii.txt", import.meta.url);
const COLOR_MAP: Record<string, string> = {
	c1: "error",
	c2: "success",
	c3: "warning",
	c4: "mdLink",
	c5: "text",
	c6: "accent",
};

let cachedAsciiSource: string | null = null;

const ANSI_PATTERN = /\x1b\[[0-9;]*m/g;

function getAsciiSource(): string {
	if (cachedAsciiSource === null) {
		cachedAsciiSource = readFileSync(ASCII_PATH, "utf8");
	}
	return cachedAsciiSource;
}

function visibleWidth(value: string): number {
	return value.replace(ANSI_PATTERN, "").length;
}

function truncateToWidth(value: string, width: number): string {
	if (width <= 0) {
		return "";
	}

	let rendered = "";
	let visible = 0;
	let index = 0;

	while (index < value.length && visible < width) {
		const ansiMatch = value.slice(index).match(/^\x1b\[[0-9;]*m/);
		if (ansiMatch) {
			rendered += ansiMatch[0];
			index += ansiMatch[0].length;
			continue;
		}

		rendered += value[index];
		visible += 1;
		index += 1;
	}

	return rendered;
}

function renderAsciiLine(theme: ThemeLike, line: string, bold: boolean): string {
	let currentColor = "text";
	let rendered = "";
	let cursor = 0;
	const pattern = /\$\{(c[1-6])\}/g;

	for (const match of line.matchAll(pattern)) {
		const token = match[1];
		const index = match.index ?? 0;
		if (index > cursor) {
			rendered += theme.fg(currentColor, line.slice(cursor, index));
		}
		currentColor = COLOR_MAP[token] ?? "text";
		cursor = index + match[0].length;
	}

	if (cursor < line.length) {
		rendered += theme.fg(currentColor, line.slice(cursor));
	}

	return bold && theme.bold ? theme.bold(rendered) : rendered;
}

export function renderAsciiLogoLines(theme: ThemeLike, options?: { bold?: boolean }): string[] {
	const bold = options?.bold === true;
	return getAsciiSource()
		.replace(/\r/g, "")
		.split("\n")
		.map((line) => renderAsciiLine(theme, line, bold));
}

export function composeHeaderLines(logoLines: string[], versionLine: string, width: number): string[] {
	if (logoLines.length === 0) {
		return [truncateToWidth(versionLine, width, "")];
	}

	const logoWidth = Math.max(...logoLines.map((line) => visibleWidth(line)), 0);
	const gap = logoWidth > 0 ? 3 : 0;
	const versionWidth = visibleWidth(versionLine);
	const targetIndex = Math.floor((logoLines.length - 1) / 2);

	return logoLines.map((line, index) => {
		if (index !== targetIndex) {
			return truncateToWidth(line, width, "");
		}

		const base = truncateToWidth(line, width, "");
		const baseWidth = visibleWidth(base);
		if (baseWidth + gap + versionWidth > width) {
			return truncateToWidth(base, width, "");
		}

		return `${base}${" ".repeat(gap)}${versionLine}`;
	});
}
