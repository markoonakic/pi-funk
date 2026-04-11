import type { AnimationDef } from "./animations.js";

type LoaderLike = {
	frames: string[];
	currentFrame: number;
	intervalId: ReturnType<typeof setInterval> | null;
	updateDisplay(): void;
	stop(): void;
	start?(): void;
	__funkyUiSpinnerPatched?: boolean;
};

export function patchLoaderPrototype(proto: LoaderLike, animation: AnimationDef): void {
	if ((proto as LoaderLike).__funkyUiSpinnerPatched) {
		return;
	}

	(proto as LoaderLike).__funkyUiSpinnerPatched = true;

	proto.start = function start(this: LoaderLike): void {
		this.stop();
		this.frames = [...animation.frames];
		this.currentFrame = 0;
		this.updateDisplay();
		this.intervalId = setInterval(() => {
			this.currentFrame = (this.currentFrame + 1) % this.frames.length;
			this.updateDisplay();
		}, animation.interval);
	};
}
