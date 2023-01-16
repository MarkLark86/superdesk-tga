import * as React from 'react';

import {IConfigComponentProps} from 'superdesk-api';
import {superdesk} from '../../superdesk';
import {Switch} from 'superdesk-ui-framework/react';
import {IProfileTextFieldConfig} from './interfaces';

type IProps = IConfigComponentProps<IProfileTextFieldConfig>;

const {Spacer} = superdesk.components;


export class ProfileTextFieldConfig extends React.PureComponent<IProps> {
    render() {
        const config = this.props.config ?? {
            use_editor_3: false,
            exclude_from_content_api: false,
        };
        const {gettext} = superdesk.localization;

        return (
            <Spacer type="vertical" spacing="medium">
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
                <Switch
                    label={{text: gettext('Exclude from ContentAPI')}}
                    value={config?.exclude_from_content_api == true}
                    onChange={(exclude_from_content_api) => {
                        this.props.onChange({
                            ...config,
                            exclude_from_content_api: exclude_from_content_api,
                        })
                    }}
                />
            </Spacer>
        );
    }
}
