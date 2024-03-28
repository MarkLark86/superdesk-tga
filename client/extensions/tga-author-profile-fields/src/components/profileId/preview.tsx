import * as React from 'react';

import {ICommonFieldConfig, IPreviewComponentProps, IUser} from 'superdesk-api';
import {IProfileIdValue} from './editor';
import {superdesk} from '../../superdesk';

type IProps = IPreviewComponentProps<IProfileIdValue, ICommonFieldConfig>;

interface IState {
    user?: IUser;
}

export class ProfileIdPreview extends React.PureComponent<IProps, IState> {
    constructor(props: IProps) {
        super(props);

        this.state = {user: undefined};
    }

    componentDidMount() {
        if (this.props.value != null) {
            const {dataApi} = superdesk;

            dataApi.findOne<IUser>('users', this.props.value).then((user) => {
                this.setState({user: user});
            });
        }
    }

    render() {
        const {UserAvatar, Spacer} = superdesk.components;

        return this.props.value == null || this.state.user == null ? null : (
            <div className="form__row">
                {/*Mimics same layout as the SelectUser component's dropdown, taken from client-core*/}
                <Spacer h={true} gap="8" noWrap={true} justifyContent="start">
                    <div>
                        <UserAvatar userId={this.props.value} />
                    </div>
                    <Spacer v={true} gap="4" noWrap={true}>
                        <div>{this.state.user.display_name}</div>
                        <div style={{fontSize: '1.2rem'}}>@{this.state.user.username}</div>
                    </Spacer>
                </Spacer>
            </div>
        );
    }
}
