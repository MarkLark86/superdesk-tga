import * as React from 'react';

import {IPreviewComponentProps} from 'superdesk-api';
import {IUserSignOff} from '../../interfaces';
import {superdesk} from '../../superdesk';

import {hasUserSignedOff} from '../../utils';

import {IconLabel, ToggleBox} from 'superdesk-ui-framework/react';
import {SignOffDetails} from '../details';

type IProps = IPreviewComponentProps<IUserSignOff | null>;

export class UserSignOffPreview extends React.PureComponent<IProps> {
    render() {
        const {gettext} = superdesk.localization;
        const sign_off_data = this.props.item.extra?.publish_sign_off;
        const isSignedOff = hasUserSignedOff(sign_off_data);

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
                        <SignOffDetails signOff={sign_off_data} />
                    </div>
                    {!sign_off_data?.funding_source?.length ? null : (
                        <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                            <label className="form-label form-label--block">Funding Source:</label>
                            <span>{sign_off_data.funding_source}</span>
                        </div>
                    )}
                    {!sign_off_data?.affiliation?.length ? null : (
                        <div className="sd-display-flex-column sd-margin-l--5 sd-padding-l--0-5 sd-margin-t--1">
                            <label className="form-label form-label--block">Affiliation:</label>
                            <span>{sign_off_data.affiliation}</span>
                        </div>
                    )}
                </ToggleBox>
            </div>
        );
    }
}
