import {
	useEffect,
	useRef,
	useState
} from "react";


import {
	type BoardConfig,
	type Position,
	type Wall,
	type SolutionPath,
} from "../types/board";


import {
	type EditMode
} from "../types/grid";



interface GridProps {

	board: BoardConfig;

	solution: SolutionPath | null;

	editMode: EditMode;


	onCellClick:
	(position: Position) => void;


	onWallClick:
	(wall: Wall) => void;
}



const MAX_GRID_PIXELS = 600;
const MIN_GRID_PIXELS = 300;



export default function Grid(
	{
		board,
		solution,
		editMode,
		onCellClick,
		onWallClick
	}: GridProps
) {


	const canvasRef =
		useRef<HTMLCanvasElement | null>(null);


	const containerRef =
		useRef<HTMLDivElement | null>(null);



	const [containerWidth, setContainerWidth] =
		useState(0);



	const [hoveredCell, setHoveredCell] =
		useState<number | null>(null);



	/*
	 * ============================
	 * Resize handling
	 * ============================
	 */

	useEffect(() => {


		function measure() {

			if (!containerRef.current)
				return;


			const width =
				containerRef.current
					.offsetWidth;


			setContainerWidth(
				Math.max(
					MIN_GRID_PIXELS,
					width - 48
				)
			);
		}



		measure();


		window.addEventListener(
			"resize",
			measure
		);


		return () =>
			window.removeEventListener(
				"resize",
				measure
			);


	}, []);




	const gridPixels =
		Math.min(
			containerWidth,
			MAX_GRID_PIXELS
		);


	const cellSize =
		gridPixels / board.boardSize;





	/*
	 * ============================
	 * Helpers
	 * ============================
	 */


	function getWaypoint(
		row: number,
		col: number
	) {

		return board.waypoints.find(
			waypoint =>
				waypoint.position.row === row &&
				waypoint.position.col === col
		);

	}




	function hasWall(
		row: number,
		col: number,
		direction: "RIGHT" | "BOTTOM"
	) {


		return board.walls.some(
			wall => {


				const a =
					wall.neighborA;


				const b =
					wall.neighborB;



				if (direction === "RIGHT") {

					return (

						(
							a.row === row &&
							a.col === col &&
							b.row === row &&
							b.col === col + 1
						)

						||

						(
							b.row === row &&
							b.col === col &&
							a.row === row &&
							a.col === col + 1
						)

					);

				}



				return (

					(
						a.row === row &&
						a.col === col &&
						b.row === row + 1 &&
						b.col === col
					)

					||

					(
						b.row === row &&
						b.col === col &&
						a.row === row + 1 &&
						a.col === col
					)

				);


			}
		);

	}





	function createWall(
		row: number,
		col: number,
		direction: "RIGHT" | "BOTTOM"
	): Wall {


		if (direction === "RIGHT") {

			return {

				neighborA: {
					row,
					col
				},

				neighborB: {
					row,
					col: col + 1
				}

			};

		}



		return {

			neighborA: {
				row,
				col
			},

			neighborB: {
				row: row + 1,
				col
			}

		};

	}





	/*
	 * ============================
	 * Solution drawing
	 * ============================
	 */


	useEffect(() => {


		const canvas =
			canvasRef.current;


		if (!canvas || gridPixels === 0)
			return;



		const ctx =
			canvas.getContext("2d");


		if (!ctx)
			return;



		canvas.width =
			gridPixels;


		canvas.height =
			gridPixels;



		ctx.clearRect(
			0,
			0,
			gridPixels,
			gridPixels
		);



		if (!solution || solution.length < 2)
			return;



		ctx.lineWidth =
			Math.max(
				2,
				cellSize * 0.15
			);


		ctx.lineCap =
			"round";


		ctx.lineJoin =
			"round";



		for (
			let i = 1;
			i < solution.length;
			i++
		) {


			const previous =
				solution[i - 1];


			const current =
				solution[i];



			ctx.beginPath();


			ctx.moveTo(
				previous.col * cellSize +
				cellSize / 2,

				previous.row * cellSize +
				cellSize / 2
			);



			ctx.lineTo(
				current.col * cellSize +
				cellSize / 2,

				current.row * cellSize +
				cellSize / 2
			);



			const progress =
				i / solution.length;



			const hue =
				50 - progress * 40;



			ctx.strokeStyle =
				`hsl(${hue},100%,60%)`;



			ctx.stroke();

		}


	},
		[
			solution,
			gridPixels,
			cellSize
		]);





	/*
	 * ============================
	 * Render
	 * ============================
	 */


	return (

		<div
			ref={containerRef}
			className="
                flex
                justify-center
                w-full
            "
		>


			<div

				className="
                    relative
                    rounded-xl
                    overflow-hidden
                    shadow-lg
                    border
                    border-border
                    bg-surface
                "

				style={{
					width: gridPixels,
					height: gridPixels
				}}

			>



				{/* Solution layer */}

				<canvas

					ref={canvasRef}

					className="
                        absolute
                        inset-0
                        z-20
                        pointer-events-none
                    "

				/>





				{/* Grid cells */}

				<div

					className="
                        grid
                        w-full
                        h-full
                    "

					style={{
						gridTemplateColumns:
							`repeat(${board.boardSize},1fr)`,

						gridTemplateRows:
							`repeat(${board.boardSize},1fr)`
					}}

				>



					{
						Array.from(
							{
								length:
									board.boardSize *
									board.boardSize
							}
						)
							.map((_, index) => {


								const row =
									Math.floor(
										index /
										board.boardSize
									);


								const col =
									index %
									board.boardSize;



								const waypoint =
									getWaypoint(
										row,
										col
									);



								const hovered =
									hoveredCell === index;



								const rightWall =
									hasWall(
										row,
										col,
										"RIGHT"
									);


								const bottomWall =
									hasWall(
										row,
										col,
										"BOTTOM"
									);



								return (

									<div

										key={index}

										className={`
                                        relative
                                        flex
                                        items-center
                                        justify-center
                                        border
                                        border-border
                                        cursor-pointer
                                        transition-colors
                                        duration-150

                                        ${hovered &&
												editMode === "NUMBERS"
												?
												"bg-orange-50"
												:
												"bg-white"
											}
                                    `}


										onMouseEnter={() =>
											setHoveredCell(index)
										}


										onMouseLeave={() =>
											setHoveredCell(null)
										}



										onClick={() => {

											if (
												editMode === "NUMBERS"
											) {
												onCellClick({
													row,
													col
												});
											}

										}}


										style={{

											width: cellSize,
											height: cellSize

										}}

									>




										{
											waypoint &&

											<div

												className="
                                                rounded-full
                                                bg-primary
                                                text-white
                                                flex
                                                items-center
                                                justify-center
                                                font-semibold
                                            "

												style={{

													width:
														cellSize * 0.58,

													height:
														cellSize * 0.58,

													fontSize:
														cellSize * 0.28

												}}

											>

												{
													waypoint.number
												}

											</div>
										}






										{/* Right wall zone */}

										{
											editMode === "WALLS" &&
											col < board.boardSize - 1 &&

											<div

												className="
                                                absolute
                                                top-0
                                                bottom-0
                                                -right-2
                                                w-4
                                                z-40
                                                cursor-pointer
                                            "

												onClick={(event) => {

													event.stopPropagation();

													onWallClick(
														createWall(
															row,
															col,
															"RIGHT"
														)
													);

												}}

											/>

										}






										{/* Bottom wall zone */}

										{
											editMode === "WALLS" &&
											row < board.boardSize - 1 &&

											<div

												className="
                                                absolute
                                                left-0
                                                right-0
                                                -bottom-2
                                                h-4
                                                z-40
                                                cursor-pointer
                                            "

												onClick={(event) => {

													event.stopPropagation();

													onWallClick(
														createWall(
															row,
															col,
															"BOTTOM"
														)
													);

												}}

											/>

										}






										{/* Wall visuals */}

										{
											rightWall &&

											<div

												className="
                                                absolute
                                                top-0
                                                bottom-0
                                                right-0
                                                w-1
                                                bg-gray-950
                                                z-30
                                            "

											/>

										}



										{
											bottomWall &&

											<div

												className="
                                                absolute
                                                left-0
                                                right-0
                                                bottom-0
                                                h-1
                                                bg-gray-950
                                                z-30
                                            "

											/>

										}



									</div>

								);


							})
					}



				</div>



			</div>


		</div>

	);

}