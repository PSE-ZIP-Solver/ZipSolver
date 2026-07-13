import {
    type AppMessage
} from "../types/message";


interface DialogPanelProps {

    message: AppMessage;

}


export default function DialogPanel(
    {
        message
    }: DialogPanelProps
) {



    const styles = {

        SUCCESS: {
            container:
                "border-green-300 bg-green-50 text-green-800",

            icon:
                "✓"
        },


        ERROR: {
            container:
                "border-red-300 bg-red-50 text-red-800",

            icon:
                "✕"
        },


        WARNING: {
            container:
                "border-yellow-300 bg-yellow-50 text-yellow-800",

            icon:
                "!"
        },


        INFO: {
            container:
                "border-blue-300 bg-blue-50 text-blue-800",

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

                    bg-white

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