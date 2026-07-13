import {
	type AppMessage,
} from "../types/message";

export interface DialogPanelProps {
	message: AppMessage | null;
}

export default function DialogPanel({
	message,
}: DialogPanelProps) {

	return (
		<div className="rounded-xl border border-slate-200 p-4 text-sm">
			<div className="font-semibold text-slate-900">Dialog placeholder</div>
			{message ? (
				<div className="mt-2">
					<div>Type: {message.type}</div>
					<div>Text: {message.message}</div>
				</div>
			) : (
				<div className="mt-2 text-slate-500">No message</div>
			)}
		</div>
	);
}
