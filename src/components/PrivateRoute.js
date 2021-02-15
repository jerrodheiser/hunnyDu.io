import React from 'react';
import { Route, Redirect } from 'react-router-dom';
import { Consumer } from './Context';
import Cookies from 'js-cookie';


// Route component that prevents rendering routes to unauthenticated users.
export default ({ component: Component, ...rest }) => {
  return (
    <Consumer>
      { context => (
        <Route
          {...rest}
          render={props => Cookies.getJSON('apiToken') ? (
              <Component {...props} />
            ) : (
              /* This sets the this.props.location.state.from value to the
                location that was denied originally.*/
              <Redirect to={{
                pathname:'/login',
                state: {from: props.location},
              }} />
            )
          }
        />
      )}
    </Consumer>
  );
};
