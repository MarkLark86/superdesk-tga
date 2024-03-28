import * as React from 'react';

import {ICommonFieldConfig, IEditorComponentProps, IUser} from 'superdesk-api';
import {superdesk} from '../../superdesk';

export type IProfileIdValue = string | undefined;
type IProps = IEditorComponentProps<IProfileIdValue, ICommonFieldConfig, never>;

export class ProfileIDField extends React.PureComponent<IProps> {
    private _mounted: boolean = false;

    constructor(props: IProps) {
        super(props);

        this.changeProfileId = this.changeProfileId.bind(this);
    }

    componentDidMount() {
        this._mounted = true;
        if (this.props.value == null) {
            superdesk.session.getCurrentUser().then((user) => {
                if (this._mounted) {
                    this.changeProfileId(user);
                }
            });
        }
    }

    componentWillUnmount() {
        this._mounted = false;
    }

    changeProfileId(user: IUser) {
        if (this._mounted) {
            this.props.onChange(user._id);
            window.dispatchEvent(new CustomEvent('content--custom-profile-id--changed', {detail: user}));
        }
    }

    render() {
        const {SelectUser} = superdesk.components;

        return (
            <SelectUser
                onSelect={this.changeProfileId}
                selectedUserId={this.props.value}
                disabled={this.props.readOnly}
                autoFocus={false}
                horizontalSpacing={false}
                clearable={false}
            />
        );
    }
}
