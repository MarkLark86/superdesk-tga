import * as React from 'react';

import {IEditorProps} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {hasUserSignedOff} from '../../utils';

import {Button, ButtonGroup} from 'superdesk-ui-framework/react';
import {getUserSignOffModal} from '../modal';
import {SignOffDetails} from '../details';

interface IState {
    showModal: boolean;
}

export class UserSignOffField extends React.Component<IEditorProps, IState> {
    constructor(props: IEditorProps) {
        super(props);

        this.showModal = this.showModal.bind(this);
        this.removeSignOff = this.removeSignOff.bind(this);

        this.state = {showModal: false};
    }

    componentDidMount() {
        if (this.props.value?.user_id == null) {
            this.props.setValue({
                consent_publish: false,
                consent_disclosure: false,
            });
        }
    }

    showModal() {
        const {showModal} = superdesk.ui;
        const {getCurrentUser} = superdesk.session;

        getCurrentUser().then((currentUser) => {
            const Modal = getUserSignOffModal(this.props, currentUser);
            showModal(Modal);
        })
    }

    removeSignOff() {
        const {confirm} = superdesk.ui;

        confirm('Are you sure you want to remove this publishing sign off?', 'Remove publishing sign off')
            .then((response) => {
                if (response) {
                    this.props.setValue({
                        consent_publish: false,
                        consent_disclosure: false,
                        user_id: null,
                        funding_source: null,
                        affiliation: null,
                        sign_date: null,
                    });
                }
            })
    }

    render() {
        const {gettext} = superdesk.localization;
        const {getCurrentUserId} = superdesk.session;

        const isSameUser = getCurrentUserId() === this.props.value?.user_id;

        return (
            <div className="sd-display-flex-column">
                <div className="sd-d-flex sd-flex-align-items-center">
                    <SignOffDetails signOff={this.props.value} />
                    {!hasUserSignedOff(this.props.value) ? (
                        <Button
                            type="warning"
                            icon="warning-sign"
                            text={gettext('Sign Off')}
                            onClick={this.showModal}
                            expand={true}
                            disabled={this.props.readOnly}
                        />
                    ) : (
                        <ButtonGroup align="right">
                            {this.props.readOnly ? null : (
                                <Button
                                    type="default"
                                    text={gettext('Remove')}
                                    icon="trash"
                                    onClick={this.removeSignOff}
                                />
                            )}
                            {(this.props.readOnly || !isSameUser) ? null : (
                                <Button
                                    type="primary"
                                    text={gettext('Edit')}
                                    icon="pencil"
                                    onClick={this.showModal}
                                />
                            )}
                        </ButtonGroup>
                    )}
                </div>
                {!this.props.value?.funding_source?.length ? null : (
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">Funding Source:</label>
                        <span>{this.props.value.funding_source}</span>
                    </div>
                )}

                {!this.props.value?.affiliation?.length ? null : (
                    <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                        <label className="form-label form-label--block">Affiliation:</label>
                        <span>{this.props.value.affiliation}</span>
                    </div>
                )}
            </div>
        );
    }
}
