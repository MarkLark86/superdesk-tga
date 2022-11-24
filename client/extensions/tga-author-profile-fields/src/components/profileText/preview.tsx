import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {FormLabel} from 'superdesk-ui-framework/react';

export class ProfileTextPreview extends React.PureComponent<IPreviewComponentProps> {
    render() {
        return (
            <div className="form__row form__row--small-padding">
                <FormLabel
                    text={this.props.field.display_name}
                    style="light"
                />
                <div dangerouslySetInnerHTML={{__html: this.props.value}} />
            </div>
        );
    }
}
