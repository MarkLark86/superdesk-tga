import {IEditorComponentProps} from 'superdesk-api';

export interface IUserSignOff {
    user_id?: string | null;
    sign_date?: string | null;

    funding_source?: string | null;
    affiliation?: string | null;

    consent_publish: boolean;
    consent_disclosure: boolean;
}

export type IEditorProps = IEditorComponentProps<IUserSignOff | null, {}>;
