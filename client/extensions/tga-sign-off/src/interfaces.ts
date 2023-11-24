import {IEditorComponentProps, IUser} from 'superdesk-api';

export interface IAuthorSignOffData {
    user_id: IUser['_id'];
    sign_date: string;
    version_signed: number;

    article_name: string;
    funding_source: string;
    affiliation: string;
    copyright_terms: string;

    author: {
        name: string;
        title: string;
        institute: string;
        email: string;
        country: string;
        orcid_id?: string;
    };

    warrants: {
        no_copyright_infringements: boolean;
        indemnify_360_against_loss: boolean;
        ready_for_publishing: boolean;
    };
    consent: {
        signature: string;
        contact: boolean;
        personal_information: boolean;
        multimedia_usage: boolean;
    };
}

export interface IPublishSignOff {
    requester_id: IUser['_id'];
    request_sent: string; // datetime string
    pending_reviews: Array<{
        user_id: IUser['_id'];
        sent: string; // datetime string
        expires: string; // datetime string
    }>;
    sign_offs: Array<IAuthorSignOffData>;
}

export type IEditorProps = IEditorComponentProps<IPublishSignOff | null, {}>;
