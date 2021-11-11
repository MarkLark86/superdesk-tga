import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {IUserSignOff} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {hasUserSignedOff} from '../../utils';

import {IconLabel, ToggleBox} from 'superdesk-ui-framework/react';
import {SignOffDetails} from '../details';

interface IProps extends IPreviewComponentProps {
    value: IUserSignOff | null;
}

export class UserSignOffPreview extends React.PureComponent<IProps> {
    render() {
        const {gettext} = superdesk.localization;
        const isSignedOff = hasUserSignedOff(this.props.value);

        return (
            <div className="sd-display-flex-column">
                <ToggleBox
                    title={gettext('Sign Off Details')}
                    className="sd-margin-b--2"
                    initiallyOpen={true}
                >
                    <IconLabel
                        text={isSignedOff ? gettext('Signed Off') : gettext('Not Signed Off')}
                        icon={isSignedOff ? 'ok' : 'warning-sign'}
                        type={isSignedOff ? 'success' : 'warning'}
                        style="translucent"
                    />
                    <div className="sd-d-flex sd-flex-align-items-center">
                        <SignOffDetails signOff={this.props.value} />
                    </div>
                    {!this.props.value?.funding_source?.length ? null : (
                        <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                            <label className="form-label form-label--block">Funding Source:</label>
                            <span>{this.props.value.funding_source}</span>
                        </div>
                    )}
                    {!this.props.value?.affiliation?.length ? null : (
                        <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                            <label className="form-label form-label--block">Affiliation:</label>
                            <span>{this.props.value.affiliation}</span>
                        </div>
                    )}
                </ToggleBox>
            </div>
        );
    }
}
