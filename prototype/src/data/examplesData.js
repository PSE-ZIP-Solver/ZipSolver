// Predefined maze examples for different grid sizes
// Uses unified format: boardSize, waypoints (array of [row, col]), walls (array of neighborA/neighborB)

export const mazesExamples = {
    3: [
        {
            id: "maze-3x3-1",
            name: "Dmitrii's Oasis",
            boardSize: 3,
            waypoints: [[0, 0], [1, 1], [2, 2]],
            walls: [
                { neighborA: [1, 0], neighborB: [1, 1] },
                { neighborA: [1, 1], neighborB: [1, 2] }
            ]
        },
        {
            id: "maze-3x3-2",
            name: "Dmitrii's Void",
            boardSize: 3,
            waypoints: [
                [0, 2],
                [1, 1]
            ],
            walls: []
        }
    ],

    4: [
        {
            id: "maze-4x4-1",
            name: "Samoon's Dream",
            boardSize: 4,
            waypoints: [[0, 3], [1, 3], [2, 0], [0, 0]],
            walls: [
                { neighborA: [0, 3], neighborB: [1, 3] },
                { neighborA: [0, 0], neighborB: [1, 0] }
            ]
        },
        {
            id: "maze-4x4-2",
            name: "Samoon's Nightmare",
            boardSize: 4,
            waypoints: [
                [3, 0],
                [2, 1],
                [1, 2],
                [0, 2]
            ],
            walls: []
        }
    ],

    5: [
        {
            id: "maze-5x5-1",
            name: "Franz's Hope",
            boardSize: 5,
            waypoints: [[0, 0], [4, 4]],
            walls: [
                { neighborA: [1, 1], neighborB: [1, 2] },
                { neighborA: [2, 0], neighborB: [2, 1] },
                { neighborA: [3, 1], neighborB: [3, 2] },
                { neighborA: [2, 3], neighborB: [2, 4] }
            ]
        },
        {
            id: "maze-5x5-2",
            name: "Franz's Doom",
            boardSize: 5,
            waypoints: [
                [0, 0],
                [1, 4],
                [4, 0],
                [2, 2],
                [3, 3],
                [3, 1]
            ],
            walls: [
                { neighborA: [0, 2], neighborB: [1, 2] },
                { neighborA: [3, 2], neighborB: [4, 2] },
                { neighborA: [2, 0], neighborB: [2, 1] },
                { neighborA: [2, 3], neighborB: [2, 4] }
            ]
        }
    ],

    6: [
        {
            id: "maze-6x6-1",
            name: "Tillmann's Glory",
            boardSize: 6,
            waypoints: [[1, 1], [1, 4], [4, 4], [4, 1]],
            walls: [
                { neighborA: [2, 4], neighborB: [3, 4] },
                { neighborA: [2, 1], neighborB: [3, 1] },
                { neighborA: [2, 3], neighborB: [2, 4] },
                { neighborA: [3, 1], neighborB: [3, 2] },
                { neighborA: [1, 2], neighborB: [1, 3] },
                { neighborA: [4, 2], neighborB: [4, 3] }
            ]
        },
        {
            id: "maze-6x6-2",
            name: "Tillmann's Torment",
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
    ],

    7: [
        {
            id: "maze-7x7-1",
            name: "Vincent's Heaven",
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
        },
        {
            id: "maze-7x7-2",
            name: "Vincent's Hell",
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
    ],

    8: [
        {
            id: "maze-8x8-1",
            name: "Henrik's Order",
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
        },
        {
            id: "maze-8x8-2",
            name: "Henrik's Madness",
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
    ],

    9: [
        {
            id: "maze-9x9-1",
            name: "M.A.Z.E.",
            boardSize: 9,
            waypoints: [
                [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8],
                [1, 8], [1, 7], [1, 6], [1, 5], [1, 4], [1, 3], [1, 2], [1, 1], [1, 0],
                [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8],
                [3, 8], [3, 7], [3, 6], [3, 5], [3, 4], [3, 3], [3, 2], [3, 1], [3, 0],
                [4, 0], [4, 1], [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [4, 8],
                [5, 8], [5, 7], [5, 6], [5, 5], [5, 4], [5, 3], [5, 2], [5, 1], [5, 0],
                [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [6, 8],
                [7, 8], [7, 7], [7, 6], [7, 5], [7, 4], [7, 3], [7, 2], [7, 1], [7, 0],
                [8, 0], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [8, 7], [8, 8]
            ],
            walls: []
        },
        {
            id: "maze-9x9-2",
            name: "Don't touch me",
            boardSize: 9,
            waypoints: [[0, 0], [8, 8]],
            walls: []
        }
    ]
};

// Get examples for a specific grid size
export const getExamplesForSize = (size) => {
    return mazesExamples[size] || [];
};

// Get all available sizes
export const getAvailableSizes = () => {
    return Object.keys(mazesExamples).map(Number).sort((a, b) => a - b);
};