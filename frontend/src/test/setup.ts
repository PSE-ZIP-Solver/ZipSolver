import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
	clearRect: vi.fn(),
	setTransform: vi.fn(),
	beginPath: vi.fn(),
	closePath: vi.fn(),
	moveTo: vi.fn(),
	lineTo: vi.fn(),
	stroke: vi.fn(),
	fill: vi.fn(),
	arc: vi.fn(),
	fillRect: vi.fn(),
	save: vi.fn(),
	restore: vi.fn(),
})) as unknown as typeof HTMLCanvasElement.prototype.getContext;