import {
	type SolverMetrics
} from "../types/solver";


interface MetricsPanelProps {
	metrics: SolverMetrics | null;
}


function formatMetricName(
	key: string
) {
	return key
		.replace(/([A-Z])/g, " $1")
		.replace(/^./, char => char.toUpperCase());
}


function formatValue(
	key: string,
	value: unknown
) {

	if (
		key.toLowerCase().includes("time") ||
		key.toLowerCase().includes("runtime")
	) {
		return `${value} ms`;
	}

	return String(value);
}


const accents = [
	"text-primary",
	"text-[var(--color-metric-accent-2)]",
	"text-[var(--color-metric-accent-3)]",
	"text-[var(--color-metric-accent-4)]",
];


const defaultMetrics: SolverMetrics = {
	runtimeMs: 0,
	steps: 0,
	attempts: 0,
};


export default function MetricsPanel({
	metrics
}: MetricsPanelProps) {


	const displayedMetrics =
		metrics ?? defaultMetrics;


	const entries =
		Object.entries(displayedMetrics);



	return (

		<div
			className="
                bg-surface/70
                backdrop-blur-md

                border
                border-footer-border

                rounded-2xl

                p-4

                shadow-md
            "
		>

			<h3
				className="
                    text-sm
                    font-bold
                    uppercase
                    tracking-wide
                    text-text
                    mb-4
                "
			>
				Solver Metrics
			</h3>



			<div
				className="
                    grid
                    grid-cols-2
                    gap-3
                "
			>

				{
					entries.map(
						([key, value], index) => (

							<div
								key={key}

								className="
                                    rounded-xl

                                    border
                                    border-footer-border

                                    bg-background/60

                                    p-3

                                    transition-all
									ui-transition

                                    hover:scale-[1.02]
                                    hover:shadow-md
                                "
							>

								<p
									className="
                                        text-xs
                                        font-semibold
                                        text-footer-text
                                        mb-1
                                    "
								>
									{formatMetricName(key)}
								</p>


								<p
									className={`
                                        text-xl
                                        font-bold
                                        ${accents[
										index % accents.length
										]
										}
                                    `}
								>
									{
										formatValue(
											key,
											value
										)
									}
								</p>

							</div>

						)
					)
				}

			</div>

		</div>

	);
}