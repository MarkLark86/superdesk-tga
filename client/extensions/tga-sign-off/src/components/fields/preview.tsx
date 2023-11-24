import * as React from 'react';

import {IPreviewComponentProps, IUser} from 'superdesk-api';
import {IAuthorSignOffData} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {loadUsersFromPublishSignOff, getSignOffDetails, viewSignOffApprovalForm} from '../../utils';

import {IconLabel, ToggleBox} from 'superdesk-ui-framework/react';
import {SignOffListItem} from '../SignOffListItem';
import {SignOffRequestDetails} from '../SignOffRequestDetails';

type IProps = IPreviewComponentProps<IAuthorSignOffData | null>;
type ISignOffState = 'completed' | 'partially' | 'none';

function getSignOffStateLabel(state: ISignOffState): string {
    const {gettext} = superdesk.localization;

    switch (state) {
        case 'completed':
            return gettext('Signed Off');
        case 'partially':
            return gettext('Partially Signed Off');
        case 'none':
            return gettext('Not Signed Off');
    }
}

interface IState {
    users: {[userId: string]: IUser};
}

export class UserSignOffPreview extends React.PureComponent<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {users: {}};
    }

    componentDidMount() {
        loadUsersFromPublishSignOff(this.props.item).then((users) => {
            this.setState({users: users});
        });
    }

    render() {
        const {gettext} = superdesk.localization;
        const {
            publishSignOff,
            unsentAuthorIds,
            pendingReviews,
            requestUser,
        } = getSignOffDetails(this.props.item, this.state.users);

        let signOffState: ISignOffState = 'none';

        if (publishSignOff != null) {
            signOffState = (unsentAuthorIds.length + pendingReviews.length) === 0 ? 'completed' : 'partially';
        }

        return (
            <div className="sd-display-flex-column">
                <IconLabel
                    text={getSignOffStateLabel(signOffState)}
                    icon={signOffState === 'completed' ? 'ok' : 'warning-sign'}
                    type={signOffState === 'completed' ? 'success' : 'warning'}
                    style="translucent"
                />

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
                                    readOnly={true}
                                    appendContentDivider={index < publishSignOff.sign_offs.length - 1}
                                    email={signOffData.author.email}
                                    date={signOffData.sign_date}
                                    buttonProps={[{
                                        type: 'success',
                                        text: gettext('View Form'),
                                        icon: 'external',
                                        onClick: viewSignOffApprovalForm.bind(
                                            undefined,
                                            this.props.item._id,
                                            signOffData.user_id,
                                        )
                                    }]}
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
                                    readOnly={true}
                                    appendContentDivider={true}
                                    date={pendingReview.expires}
                                />
                            )
                        ))}
                        {unsentAuthorIds.map((authorId) => (
                            this.state.users[authorId] == null ? null : (
                                <SignOffListItem
                                    state="not_sent"
                                    user={this.state.users[authorId]}
                                    readOnly={true}
                                    appendContentDivider={true}
                                />
                            )
                        ))}
                    </ToggleBox>
                )}
            </div>
        );
    }
}
