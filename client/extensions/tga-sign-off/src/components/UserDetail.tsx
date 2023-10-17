import * as React from 'react';

import {IUser} from 'superdesk-api';
import {superdesk} from "../superdesk";


interface IProps {
    user: IUser;
    label: string;
}

export function UserDetail(props: IProps) {
    const {UserAvatar} = superdesk.components;

    return (
        <React.Fragment>
            <div className="sd-margin-l--1">
                <UserAvatar userId={props.user._id} />
            </div>
            <div className="sd-display-flex-column sd-margin-l--1">
                <label className="form-label form-label--block">{props.label}</label>
                <span>{props.user.display_name}</span>
            </div>
        </React.Fragment>
    );
}
