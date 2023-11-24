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
    buttonProps?: Array<React.ComponentProps<typeof Button>>;
}

interface IPropsApproved extends IPropsBase {
    state: 'approved';
    email: string;
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
                    <React.Fragment>
                        {props.buttonProps.length === 1 ? (
                            <ButtonGroup align="end">
                                <Button
                                    key={props.buttonProps[0].text}
                                    {...props.buttonProps[0]}
                                />
                            </ButtonGroup>
                        ) : (
                            <div className="sd-margin-l--auto">
                                <ButtonGroup orientation="vertical">
                                    {props.buttonProps.map((buttonProps) => (
                                        <Button
                                            key={buttonProps.text}
                                            {...buttonProps}
                                        />
                                    ))}
                                </ButtonGroup>
                            </div>
                        )}
                    </React.Fragment>
                )}
            </div>
            {props.state !== 'approved' ? null : (
                <React.Fragment>
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">{gettext('Email:')}</label>
                        <span>{props.email.trim()}</span>
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
