import {IEditorComponentProps, IUser} from 'superdesk-api';

export interface IUserSignOff {
    requester_id: undefined;
    user_id: IUser['_id'];
    sign_date: string;
    version_signed: number;
    funding_source: string;
    affiliation: string;
    consent_publish: boolean;
    consent_disclosure: boolean;
}

export interface IPublishSignOff {
    requester_id: IUser['_id'];
    request_sent: string; // datetime string
    pending_reviews: Array<{
        user_id: IUser['_id'];
        sent: string; // datetime string
        expires: string; // datetime string
    }>;
    sign_offs: Array<IUserSignOff>;
}

export type IEditorProps = IEditorComponentProps<IPublishSignOff | null, {}>;
