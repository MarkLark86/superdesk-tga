import * as React from 'react';

import {IUser} from 'superdesk-api';
import {IEditorProps, IAuthorSignOffData, IPublishSignOff} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {
    hasUserSignedOff,
    getListAuthorIds,
    loadUsersFromPublishSignOff,
    getSignOffDetails,
    viewSignOffApprovalForm,
} from '../../utils';

import {Button, ToggleBox} from 'superdesk-ui-framework/react';
import {SignOffListItem} from '../SignOffListItem';
import {SignOffRequestDetails} from '../SignOffRequestDetails';

interface IState {
    users: {[userId: string]: IUser};
}

export class UserSignOffField extends React.Component<IEditorProps, IState> {
    constructor(props: IEditorProps) {
        super(props);

        this.state = {users: {}};

        this.removeSignOff = this.removeSignOff.bind(this);
    }

    componentDidMount() {
        this.reloadUsers();
    }

    componentDidUpdate() {
        const {signOffIds, unsentAuthorIds} = getSignOffDetails(this.props.item, this.state.users);
        const userIds = signOffIds.concat(unsentAuthorIds);
        let reloadUsers = false;

        for (let i = 0; i < userIds.length; i++) {
            if (this.state.users[userIds[i]] == null) {
                reloadUsers = true;
                break;
            }
        }

        if (reloadUsers) {
            this.reloadUsers();
        }
    }

    reloadUsers() {
        loadUsersFromPublishSignOff(this.props.item).then((users) => {
            this.setState({users: users});
        });
    }

    sendSignOff(authorIds?: Array<IUser['_id']>) {
        const {notify} = superdesk.ui;
        const {gettext} = superdesk.localization;
        const {signOffIds} = getSignOffDetails(this.props.item, this.state.users);

        if (authorIds == null) {
            authorIds = getListAuthorIds(this.props.item)
                .filter((authorId) => !signOffIds.includes(authorId));
        }

        if (authorIds.length === 0) {
            notify.error(
                signOffIds.length === 0 ?
                    gettext('Unable to send email(s), list of authors is empty!') :
                    gettext('All authors have already signed off.')
            );
            return;
        }

        superdesk.httpRequestJsonLocal({
            method: 'POST',
            path: '/sign_off_request',
            payload: {
                item_id: this.props.item._id,
                authors: authorIds,
            }
        }).then(() => {
            notify.success(gettext('Sign off request email(s) sent'));
        }, (error) => {
            notify.error(gettext('Failed to send sign off request email(s). {{ error }}', error));
        });
    }

    removeSignOff(signOffData: IAuthorSignOffData) {
        const {confirm, notify} = superdesk.ui;
        const {gettext} = superdesk.localization;
        const publishSignOff: IPublishSignOff | undefined = this.props.item.extra?.publish_sign_off;

        if (publishSignOff == null) {
            notify.error(gettext('Unable to remove sign off, no sign offs found'));
            return;
        }

        confirm(
            gettext('Are you sure you want to remove this publishing sign off?'),
            gettext('Remove publishing sign off')
        ).then((response) => {
            if (response) {
                superdesk.httpRequestVoidLocal({
                    method: 'DELETE',
                    path: `/sign_off_request/${this.props.item._id}/${signOffData.user_id}`,
                }).then(() => {
                    notify.success(gettext('Publishing sign off removed'));
                }).catch((error: string) => {
                    notify.error(gettext('Failed to remove sign off. {{ error }}', {error}))
                });
            }
        });
    }

    render() {
        const {gettext,} = superdesk.localization;
        const {
            publishSignOff,
            unsentAuthorIds,
            pendingReviews,
            requestUser,
        } = getSignOffDetails(this.props.item, this.state.users);

        return (
            <div className="sd-display-flex-column">
                {hasUserSignedOff(this.props.item) === true || this.props.readOnly ? null : (
                    <div className="sd-d-flex sd-flex-align-items-center">
                        <Button
                            type="warning"
                            icon="warning-sign"
                            text={gettext('Send Sign Off Email(s)')}
                            onClick={this.sendSignOff.bind(this, undefined)}
                            expand={true}
                            disabled={this.props.readOnly}
                        />
                    </div>
                )}

                {requestUser == null || publishSignOff?.request_sent == null ? null : (
                    <SignOffRequestDetails
                        publishSignOff={publishSignOff}
                        user={requestUser}
                    />
                )}

                {publishSignOff?.sign_offs == null || publishSignOff.sign_offs.length === 0 ? null : (
                    <ToggleBox
                        title={gettext(
                            'Approvals ({{ count }})',
                            {count: publishSignOff.sign_offs.length}
                        )}
                    >
                        {publishSignOff.sign_offs.map((signOffData, index) => (
                            this.state.users[signOffData.user_id] == null ? null : (
                                <SignOffListItem
                                    state="approved"
                                    user={this.state.users[signOffData.user_id]}
                                    readOnly={this.props.readOnly}
                                    appendContentDivider={index < publishSignOff.sign_offs.length - 1}
                                    buttonProps={this.props.readOnly ? [{
                                        type: 'success',
                                        text: gettext('View Form'),
                                        icon: 'external',
                                        onClick: viewSignOffApprovalForm.bind(
                                            undefined,
                                            this.props.item._id,
                                            signOffData.user_id
                                        ),
                                    }] : [{
                                        type: 'success',
                                        text: gettext('View Form'),
                                        icon: 'external',
                                        onClick: viewSignOffApprovalForm.bind(
                                            undefined,
                                            this.props.item._id,
                                            signOffData.user_id
                                        ),
                                    }, {
                                        type: 'default',
                                        text: gettext('Remove'),
                                        icon: 'trash',
                                        onClick: this.removeSignOff.bind(this, signOffData)
                                    }]}
                                    email={signOffData.author.email}
                                    date={signOffData.sign_date}
                                />
                            )
                        ))}
                    </ToggleBox>
                )}

                {(pendingReviews.length + unsentAuthorIds.length) === 0 ? null : (
                    <ToggleBox
                        title={gettext(
                            'Pending Approvals ({{ count }})',
                            {count: pendingReviews.length + unsentAuthorIds.length}
                        )}
                    >
                        {pendingReviews.map((pendingReview) => (
                            this.state.users[pendingReview.user_id] == null ? null : (
                                <SignOffListItem
                                    state="pending"
                                    user={this.state.users[pendingReview.user_id]}
                                    readOnly={this.props.readOnly}
                                    appendContentDivider={true}
                                    buttonProps={this.props.readOnly ? undefined : [{
                                        text: gettext('Resend'),
                                        icon: 'refresh',
                                        onClick: this.sendSignOff.bind(this, [pendingReview.user_id]),
                                    }]}
                                    date={pendingReview.expires}
                                />
                            )
                        ))}

                        {unsentAuthorIds.map((authorId) => (
                            this.state.users[authorId] == null ? null : (
                                <SignOffListItem
                                    state="not_sent"
                                    user={this.state.users[authorId]}
                                    readOnly={this.props.readOnly}
                                    appendContentDivider={true}
                                    buttonProps={this.props.readOnly ? undefined : [{
                                        text: gettext('Send'),
                                        icon: 'assign',
                                        onClick: this.sendSignOff.bind(this, [authorId]),
                                    }]}
                                />
                            )
                        ))}
                    </ToggleBox>
                )}
            </div>
        );
    }
}
