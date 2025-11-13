import streamlit as st


def main():
    st.title("Documentation")

    st.markdown(
        """
        ## Shield AI Documentation

        This section provides documentation for the Shield AI application.

        ### Overview
        Shield AI is a comprehensive solution for shrinkage forecasting and analysis in retail environments. The application provides tools for:
        - Data parsing and validation
        - Coefficient calibration
        - Shrinkage forecasting
        - Database management
        - Health monitoring
        - Configuration management

        ### Features
        - **Project Metrics**: View overall project metrics and statistics
        - **Data Parsing**: Parse and validate input data
        - **Coefficient Calibration**: Calibrate forecasting coefficients
        - **Shrinkage Forecasting**: Generate shrinkage forecasts
        - **Coefficient Analysis**: Analyze and visualize coefficients
        - **Shrinkage Analysis**: Detailed shrinkage analysis
        - **Architecture Visualization**: Visualize system architecture
        - **Database Management**: Manage database connections and operations
        - **CLI Integration**: Integrate with command-line interface
        - **Health Monitoring**: Monitor system health and performance
        - **Configuration**: Manage application configuration

        ### Usage
        Each page provides specific functionality for different aspects of shrinkage analysis and forecasting. Navigate using the sidebar to access different features.

        ### Technical Details
        The application is built using a modular architecture with clear separation of concerns:
        - **Presentation Layer**: Streamlit UI components
        - **Application Layer**: Use cases and business logic
        - **Domain Layer**: Core entities and business rules
        - **Infrastructure Layer**: Database and external service integration
        """
    )


if __name__ == "__main__":
    main()