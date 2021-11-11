import {IUserSignOff} from "./interfaces";

export function hasUserSignedOff(signOff: IUserSignOff | null): boolean {
    return signOff != null &&
        signOff.user_id != null &&
        signOff.consent_publish == true &&
        signOff.consent_disclosure == true;
}
