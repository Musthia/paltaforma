export const parseJwt = (token) => {

    try {

        const base64 = token.split(".")[1];

        return JSON.parse(
            atob(base64)
        );

    } catch {

        return null;
    }
};