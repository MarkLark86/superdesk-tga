import * as React from 'react';

import {IEditorComponentProps, IUser} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {IProfileTextFieldConfig} from './interfaces';
import {Input} from 'superdesk-ui-framework/react'

type IProps = IEditorComponentProps<string, IProfileTextFieldConfig>;

export class ProfileTextField extends React.PureComponent<IProps> {
    constructor(props: IProps) {
        super(props);

        this.onProfileIDChanged = this.onProfileIDChanged.bind(this);
    }

    componentDidMount() {
        window.addEventListener('content--custom-profile-id--changed', this.onProfileIDChanged);
    }

    componentWillUnmount() {
        window.removeEventListener('content--custom-profile-id--changed', this.onProfileIDChanged)
    }

    onProfileIDChanged(event: Event) {
        const user = (event as CustomEvent<IUser>).detail;

        switch (this.props.fieldId) {
        case 'profile_first_name':
            this.props.setValue(user.first_name || '');
            break;
        case 'profile_last_name':
            this.props.setValue(user.last_name || '');
            break;
        case 'profile_email':
            this.props.setValue(user.email || '');
            break;
        case 'profile_biography':
            this.props.setValue(user.biography || '');
            break;
        }
    }

    render() {
        const {Editor3Html} = superdesk.components;

        return this.props.config?.use_editor_3 ? (
            <Editor3Html
                key={this.props.item.extra?.profile_id}
                value={this.props.value}
                onChange={this.props.setValue}
                readOnly={this.props.readOnly}
            />
        ) : (
            <Input
                key={this.props.item.extra?.profile_id}
                value={this.props.value}
                disabled={this.props.readOnly}
                onChange={this.props.setValue}
            />
        );
    }
}
