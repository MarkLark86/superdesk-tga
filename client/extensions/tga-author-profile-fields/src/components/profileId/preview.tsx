import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {FormLabel} from 'superdesk-ui-framework/react';

export class ProfileIDPreview extends React.PureComponent<IPreviewComponentProps> {
    render() {
        const {gettext} = superdesk.localization;

        return (
            <div className="form__row form__row--small-padding">
                <FormLabel
                    text={gettext('Profile ID')}
                    style="light"
                />
                <p className="sd-text__normal">
                    {this.props.value}
                </p>
            </div>
        );
    }
}
