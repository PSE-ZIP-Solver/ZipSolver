export async function validateJsonFile(
    file: File
): Promise<boolean> {

    if (
        file.type !== "application/json"
    ) {
        return false;
    }

    try {
        const text =
            await file.text();

        JSON.parse(text);

        return true;

    } catch {
        return false;
    }
}