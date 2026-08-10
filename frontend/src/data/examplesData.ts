import { type BoardConfig } from "../types/board";

export interface ExampleBoard {
    id: string;
    name: string;
    config: BoardConfig;
}


export const Examples: ExampleBoard[] = [
   {
    id: "board-8x8-1",
    name: "Imported Board",
    config: {
        boardSize: 8,
        waypoints: [
            [3, 2],
            [1, 3],
            [3, 4],
            [5, 4],
            [1, 5],
            [4, 6],
            [6, 6],
            [3, 7]
        ],
        walls: []
    }
},
    {
        id: "maze-6x6-2",
        name: "Tillmann's Torment",
        config: {
            boardSize: 6,
            waypoints: [[0, 1], [1, 5], [5, 4], [4, 0]],
            walls: [
                { neighborA: [0, 1], neighborB: [1, 1] },
                { neighborA: [4, 4], neighborB: [5, 4] },
                { neighborA: [0, 4], neighborB: [1, 4] },
                { neighborA: [4, 1], neighborB: [5, 1] },
                { neighborA: [1, 1], neighborB: [1, 2] },
                { neighborA: [4, 3], neighborB: [4, 4] },
                { neighborA: [1, 4], neighborB: [1, 5] },
                { neighborA: [4, 0], neighborB: [4, 1] }
            ]
        }
    }, 
    {
        id: "maze-7x7-1",
        name: "Vincent's Heaven",
        config: {
            boardSize: 7,
            waypoints: [
                [3, 3],
                [2, 3],
                [2, 2],
                [3, 2],
                [4, 2],
                [4, 3],
                [4, 4],
                [3, 4],
                [2, 4]
            ],
            walls: [
                { neighborA: [1, 3], neighborB: [2, 3] },
                { neighborA: [1, 2], neighborB: [2, 2] },
                { neighborA: [4, 2], neighborB: [5, 2] },
                { neighborA: [4, 3], neighborB: [5, 3] },
                { neighborA: [4, 4], neighborB: [5, 4] },
                { neighborA: [2, 1], neighborB: [2, 2] },
                { neighborA: [3, 1], neighborB: [3, 2] },
                { neighborA: [4, 1], neighborB: [4, 2] },
                { neighborA: [4, 4], neighborB: [4, 5] }
            ]
        }
    }, 
    {
        id: "maze-7x7-2",
        name: "Vincent's Hell",
        config: {
            boardSize: 7,
            waypoints: [[5, 5], [1, 5], [1, 1], [5, 1], [3, 3]],
            walls: [
                { neighborA: [1, 3], neighborB: [2, 3] },
                { neighborA: [4, 3], neighborB: [5, 3] },
                { neighborA: [4, 2], neighborB: [5, 2] },
                { neighborA: [1, 4], neighborB: [2, 4] },
                { neighborA: [3, 1], neighborB: [3, 2] },
                { neighborA: [3, 4], neighborB: [3, 5] },
                { neighborA: [4, 1], neighborB: [4, 2] },
                { neighborA: [2, 4], neighborB: [2, 5] }
            ]
        }
    }, 
    {
        id: "maze-8x8-1",
        name: "Henrik's Order",
        config: {
            boardSize: 8,
            waypoints: [[0, 1], [0, 6]],
            walls: [
                { neighborA: [0, 1], neighborB: [0, 2] },
                { neighborA: [1, 1], neighborB: [1, 2] },
                { neighborA: [2, 1], neighborB: [2, 2] },
                { neighborA: [3, 1], neighborB: [3, 2] },
                { neighborA: [4, 1], neighborB: [4, 2] },
                { neighborA: [5, 1], neighborB: [5, 2] },
                { neighborA: [6, 1], neighborB: [6, 2] },
                { neighborA: [0, 3], neighborB: [0, 4] },
                { neighborA: [2, 3], neighborB: [2, 4] },
                { neighborA: [3, 3], neighborB: [3, 4] },
                { neighborA: [4, 3], neighborB: [4, 4] },
                { neighborA: [5, 3], neighborB: [5, 4] },
                { neighborA: [6, 3], neighborB: [6, 4] },
                { neighborA: [7, 3], neighborB: [7, 4] },
                { neighborA: [6, 5], neighborB: [6, 6] },
                { neighborA: [5, 5], neighborB: [5, 6] },
                { neighborA: [4, 5], neighborB: [4, 6] },
                { neighborA: [3, 5], neighborB: [3, 6] },
                { neighborA: [2, 5], neighborB: [2, 6] },
                { neighborA: [1, 5], neighborB: [1, 6] },
                { neighborA: [0, 5], neighborB: [0, 6] }
            ]
        }
    }, 
    {
        id: "maze-8x8-2",
        name: "Henrik's Madness",
        config: {
            boardSize: 8,
            waypoints: [
                [7, 3],
                [5, 1],
                [4, 0],
                [6, 2],
                [6, 5],
                [1, 2],
                [3, 0],
                [2, 1],
                [0, 3],
                [0, 4],
                [2, 6],
                [1, 5],
                [3, 7],
                [4, 7],
                [5, 6],
                [7, 4]
            ],
            walls: [
                { neighborA: [6, 3], neighborB: [7, 3] },
                { neighborA: [6, 1], neighborB: [7, 1] },
                { neighborA: [6, 2], neighborB: [7, 2] },
                { neighborA: [6, 4], neighborB: [7, 4] },
                { neighborA: [6, 5], neighborB: [7, 5] },
                { neighborA: [6, 6], neighborB: [7, 6] },
                { neighborA: [3, 4], neighborB: [4, 4] },
                { neighborA: [3, 3], neighborB: [4, 3] },
                { neighborA: [2, 3], neighborB: [2, 4] },
                { neighborA: [1, 3], neighborB: [1, 4] }
            ]
        }

    }
]