import {
    type AppMessage
} from "../types/message";


/** Message state displayed in the contextual status panel. */
interface DialogPanelProps {

    message: AppMessage;

}


/** Renders an application message with severity-specific styling. */
export default function DialogPanel(
    {
        message
    }: DialogPanelProps
) {



    const styles = {

        SUCCESS: {
            container:
                "alert-success",

            icon:
                "✓"
        },


        ERROR: {
            container:
                "alert-error",

            icon:
                "✕"
        },


        WARNING: {
            container:
                "alert-warning",

            icon:
                "!"
        },


        INFO: {
            container:
                "alert-info",

            icon:
                "i"
        }

    }[message.type];



    return (

        <div
            className={`
                flex
				min-h-16
                items-center
                gap-3

                rounded-lg
                border

                px-4
                py-3

                text-sm
                font-medium

                shadow-sm

                ${styles.container}
            `}
        >


            <div
                className="
                    flex
                    h-6
                    w-6
                    items-center
                    justify-center

                    rounded-full
                    dialog-icon

                    font-bold
                "
            >

                {styles.icon}

            </div>



            <p>
                {message.message}
            </p>


        </div>

    );
}