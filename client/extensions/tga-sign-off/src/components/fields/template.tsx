import * as React from 'react';

import {ITemplateEditorComponentProps, ICommonFieldConfig} from 'superdesk-api';
import {IPublishSignOffValue} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {Button} from 'superdesk-ui-framework/react';

type IProps = ITemplateEditorComponentProps<IPublishSignOffValue, ICommonFieldConfig>;

export class UserSignOffTemplate extends React.PureComponent<IProps> {
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
