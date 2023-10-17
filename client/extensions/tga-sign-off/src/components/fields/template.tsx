import * as React from 'react';

import {IEditorProps} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {Button} from 'superdesk-ui-framework/react';

export class UserSignOffTemplate extends React.PureComponent<IEditorProps> {
    render() {
        const {gettext} = superdesk.localization;

        return (
            <div className="sd-display-flex-column">
                <div className="sd-d-flex sd-flex-align-items-center">
                    <Button
                        type="warning"
                        icon="warning-sign"
                        text={gettext('Send Sign Off Email(s)')}
                        onClick={() => false}
                        expand={true}
                        disabled={this.props.readOnly}
                    />
                </div>
            </div>
        );
    }
}
