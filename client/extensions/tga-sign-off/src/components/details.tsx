import * as React from 'react';

import {IUser} from 'superdesk-api';
import {IUserSignOff} from '../interfaces';
import {superdesk} from '../superdesk';

interface IProps {
    signOff?: IUserSignOff | null;
}

interface IState {
    user?: IUser;
}

export class SignOffDetails extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {user: undefined};
    }

    componentDidMount() {
        this.loadUser();
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (prevProps.signOff?.user_id !== this.props.signOff?.user_id) {
            this.loadUser();
        }
    }

    loadUser() {
        if (this.props.signOff?.user_id == null) {
            this.setState({user: undefined});
        } else {
            const {getUsersByIds} = superdesk.entities.users;

            getUsersByIds([this.props.signOff.user_id]).then((users) => {
                this.setState({user: users[0]});
            })
        }
    }

    render() {
        const {UserAvatar} = superdesk.components;
        const {formatDateTime} = superdesk.localization;

        return this.state.user == null ? null : (
            <React.Fragment>
                <div className="sd-margin-l--1">
                    <UserAvatar userId={this.state.user._id} />
                </div>
                <div className="sd-display-flex-column sd-margin-l--1">
                    <label className="form-label form-label--block">Signed By:</label>
                    <span>{this.state.user.display_name}</span>
                </div>
                {this.props.signOff?.sign_date == null ? null : (
                    <div className="sd-display-flex-column sd-margin-l--1">
                        <label className="form-label form-label--block">Signed Date:</label>
                        <span>{formatDateTime(new Date(this.props.signOff.sign_date))}</span>
                    </div>
                )}
            </React.Fragment>
        );
    }
}
