import * as React from 'react';

import {IUser} from 'superdesk-api';
import {superdesk} from '../superdesk';

import {ButtonGroup, Button, ContentDivider} from 'superdesk-ui-framework/react';
import {UserDetail} from './UserDetail';

interface IPropsBase {
    state: 'approved' | 'pending' | 'not_sent';
    user: IUser;
    readOnly?: boolean;
    appendContentDivider?: boolean;
    buttonProps?: {
        text: string;
        icon: string;
        onClick(): void;
    };
}

interface IPropsApproved extends IPropsBase {
    state: 'approved';
    fundingSource: string;
    affiliation: string;
    date: string;
}

interface IPropsPendingOrExpired extends IPropsBase {
    state: 'pending';
    date: string;
}

interface IPropsNotSend extends IPropsBase {
    state: 'not_sent';
}

type IProps = IPropsApproved | IPropsPendingOrExpired | IPropsNotSend;

export function SignOffListItem(props: IProps) {
    const {formatDateTime, gettext} = superdesk.localization;

    return (
        <React.Fragment>
            <div className="sd-d-flex sd-flex-align-items-center">
                <UserDetail
                    user={props.user}
                    label={gettext('Author:')}
                />
                {props.state === 'not_sent' ? null : (
                    <div className="sd-display-flex-column sd-margin-l--1">
                        <label className="form-label form-label--block">
                            {props.state === 'approved' ?
                                gettext('Signed Date') :
                                gettext('Request Sent:')
                            }
                        </label>
                        <span>{formatDateTime(new Date(props.date))}</span>
                    </div>
                )}

                {props.buttonProps == null ? null : (
                    <ButtonGroup align="end">
                        <Button
                            type="default"
                            text={props.buttonProps.text}
                            icon={props.buttonProps.icon}
                            onClick={props.buttonProps.onClick}
                        />
                    </ButtonGroup>
                )}
            </div>
            {props.state !== 'approved' ? null : (
                <React.Fragment>
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">{gettext('Funding Source:')}</label>
                        <span>{props.fundingSource.trim()}</span>
                    </div>
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">{gettext('Affiliation:')}</label>
                        <span>{props.affiliation.trim()}</span>
                    </div>
                </React.Fragment>
            )}

            {props.state !== 'pending' ? null : (
                <div className="sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                    <label className="form-label form-label--block">{gettext('State:')}</label>
                    {new Date(props.date) <= new Date() ? (
                        <span>{gettext('Expired')}</span>
                    ): (
                        <span>{gettext('Pending')}</span>
                    )}
                </div>
            )}
            {props.state !== 'not_sent' ? null : (
                <div className="sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                    <label className="form-label form-label--block">{gettext('State:')}</label>
                    <span>{gettext('Not Sent')}</span>
                </div>
            )}

            {props.appendContentDivider !== true ? null : (
                <ContentDivider margin="small" />
            )}
        </React.Fragment>
    );
}
