import React from 'react';
import { Route, Redirect } from 'react-router-dom';
import { Consumer } from './Context';


// Route component that prevents rendering routes restricted to some users.
export default ({ component: Component, ...rest }) => {
  return (
    <Consumer>
      { context => (
        <Route
          {...rest}
          render={props => context.isAuthenticated && context.isLeader ? (
              <Component {...props} />
            ) : (
              <Redirect to={{
                pathname:'/'
              }} />
            )
          }
        />
      )}
    </Consumer>
  );
};
