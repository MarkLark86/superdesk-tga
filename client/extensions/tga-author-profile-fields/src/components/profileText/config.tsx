import * as React from 'react';

import {IConfigComponentProps} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {Switch} from 'superdesk-ui-framework/react';
import {IProfileTextFieldConfig} from './interfaces';

type IProps = IConfigComponentProps<IProfileTextFieldConfig>;


export class ProfileTextFieldConfig extends React.PureComponent<IProps> {
    render() {
        const config = this.props.config ?? {use_editor_3: false};
        const {gettext} = superdesk.localization;

        return (
            <Switch
                label={{text: gettext('Use Editor 3')}}
                value={config?.use_editor_3 == true}
                onChange={(use_editor_3) => {
                    this.props.onChange({
                        ...config,
                        use_editor_3: use_editor_3,
                    });
                }}
            />
        );
    }
}
