import {IUserSignOff} from "./interfaces";

export function hasUserSignedOff(signOff: IUserSignOff | null): boolean {
    return signOff != null &&
        signOff.user_id != null &&
        signOff.consent_publish &&
        signOff.consent_disclosure &&
        (signOff.funding_source ?? '').trim().length > 0 &&
        (signOff.affiliation ?? '').trim().length > 0;
}
