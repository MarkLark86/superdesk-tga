import * as React from 'react';

import {IUser} from 'superdesk-api';
import {IPublishSignOff} from '../interfaces';
import {superdesk} from '../superdesk';

interface IProps {
    publishSignOff: IPublishSignOff;
    user: IUser;
}

export function SignOffRequestDetails(props: IProps) {
    const {gettext, formatDateTime, longFormatDateTime} = superdesk.localization;

    return (
        <div className="sd-margin-t--1 sd-margin-b--2">
            {gettext('Request last sent')}&nbsp;
            <time title={longFormatDateTime(new Date(props.publishSignOff.request_sent))}>
                {formatDateTime(new Date(props.publishSignOff.request_sent))}
            </time>
            &nbsp;{gettext('by')} {props.user.display_name}
        </div>
    );
}
