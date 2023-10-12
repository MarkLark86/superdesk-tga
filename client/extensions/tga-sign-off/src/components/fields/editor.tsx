import * as React from 'react';

import {IEditorProps} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {hasUserSignedOff} from '../../utils';

import {Button, ButtonGroup} from 'superdesk-ui-framework/react';
import {SignOffDetails} from '../details';

export class UserSignOffField extends React.Component<IEditorProps> {
    constructor(props: IEditorProps) {
        super(props);

        this.removeSignOff = this.removeSignOff.bind(this);
        this.sendSignOff = this.sendSignOff.bind(this);
    }

    sendSignOff() {
        const authorIds = (this.props.item.authors ?? []).map((author) => author.parent);

        if (authorIds.length === 0) {
            superdesk.ui.notify.error(
                superdesk.localization.gettext('Unable to send email(s), list of authors is empty!')
            );
            return;
        }

        superdesk.httpRequestJsonLocal({
            method: "POST",
            path: "/sign_off_request",
            payload: {
                item_id: this.props.item._id,
                authors: authorIds,
            }
        });
    }

    removeSignOff() {
        const {confirm} = superdesk.ui;
        const {gettext} = superdesk.localization;

        confirm(gettext('Are you sure you want to remove this publishing sign off?'), gettext('Remove publishing sign off'))
            .then((response) => {
                if (response) {
                    superdesk.entities.article.patch(this.props.item, {
                        extra: {
                            ...(this.props.item.extra ?? {}),
                            publish_sign_off: {},
                        }
                    });
                }
            })
    }

    render() {
        const {gettext} = superdesk.localization;
        const {getCurrentUserId} = superdesk.session;
        const sign_off_data = this.props.item.extra?.publish_sign_off ?? {};
        const isSameUser = getCurrentUserId() === sign_off_data?.user_id;

        return (
            <div className="sd-display-flex-column">
                <div className="sd-d-flex sd-flex-align-items-center">
                    <SignOffDetails signOff={sign_off_data} />
                    {!hasUserSignedOff(sign_off_data) ? (
                        <Button
                            type="warning"
                            icon="warning-sign"
                            text={gettext('Send Sign Off Email(s)')}
                            onClick={this.sendSignOff}
                            expand={true}
                            disabled={this.props.readOnly}
                        />
                    ) : (
                        <ButtonGroup align="end">
                            {this.props.readOnly !== true && (
                                <Button
                                    type="default"
                                    text={gettext('Remove')}
                                    icon="trash"
                                    onClick={this.removeSignOff}
                                />
                            )}
                            {!(this.props.readOnly || !isSameUser) && (
                                <Button
                                    type="primary"
                                    text={gettext('Edit')}
                                    icon="pencil"
                                    onClick={this.sendSignOff}
                                />
                            )}
                        </ButtonGroup>
                    )}
                </div>
                {(sign_off_data.funding_source?.length ?? 0) > 0 && (
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">{gettext('Funding Source:')}</label>
                        <span>{sign_off_data.funding_source}</span>
                    </div>
                )}

                {(sign_off_data.affiliation?.length ?? 0) > 0 && (
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">{gettext('Affiliation:')}</label>
                        <span>{sign_off_data.affiliation}</span>
                    </div>
                )}
            </div>
        );
    }
}
