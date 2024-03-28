import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {IProfileTextFieldConfig, IProfileTextValue} from './interfaces';

type IProps = IPreviewComponentProps<IProfileTextValue, IProfileTextFieldConfig>;

export class ProfileTextPreview extends React.PureComponent<IProps> {
    render() {
        return this.props.value == null || this.props.value.length === 0 ? null : (
            <div className="form__row">
                <div dangerouslySetInnerHTML={{__html: this.props.value}} />
            </div>
        );
    }
}
