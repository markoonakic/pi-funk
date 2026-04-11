export type AnimationName = "pulse" | "waverows";

export type AnimationDef = {
	frames: readonly string[];
	interval: number;
};

export const ANIMATIONS: Record<AnimationName, AnimationDef> = {
	pulse: {
		frames: [
			"⠀⠶⠀",
			"⠰⣿⠆",
			"⢾⣉⡷",
			"⣏⠀⣹",
			"⡁⠀⢈",
		],
		interval: 180,
	},
	waverows: {
		frames: [
			"⠖⠉⠉⠑",
			"⡠⠖⠉⠉",
			"⣠⡠⠖⠉",
			"⣄⣠⡠⠖",
			"⠢⣄⣠⡠",
			"⠙⠢⣄⣠",
			"⠉⠙⠢⣄",
			"⠊⠉⠙⠢",
			"⠜⠊⠉⠙",
			"⡤⠜⠊⠉",
			"⣀⡤⠜⠊",
			"⢤⣀⡤⠜",
			"⠣⢤⣀⡤",
			"⠑⠣⢤⣀",
			"⠉⠑⠣⢤",
			"⠋⠉⠑⠣",
		],
		interval: 90,
	},
};

export function getAnimationFrame(name: AnimationName, tick: number): string {
	const animation = ANIMATIONS[name];
	return animation.frames[((tick % animation.frames.length) + animation.frames.length) % animation.frames.length] ?? "";
}
