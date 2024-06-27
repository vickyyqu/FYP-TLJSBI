import axios from "axios";

const CPI_API_URL = "https://bded5ua481.execute-api.us-east-1.amazonaws.com/FYPexposedAPI/getForecast";
const RSI_API_URL = "https://pmvxift05k.execute-api.us-east-1.amazonaws.com/exposeAPI/RSIForecast";
const SB_API_URL = "https://anpxz1s6b3.execute-api.us-east-1.amazonaws.com/exposeAPI/getSBCategories";
const DD_API_URL = "https://t5ulert62c.execute-api.us-east-1.amazonaws.com/exposeAPI/getCategoryDemand";
const GET_PROD_URL = "https://1sszg4q3hh.execute-api.us-east-1.amazonaws.com/productAPI/getAllProducts";
const GET_SINGLE_PROD = "https://ir39pxdck8.execute-api.us-east-1.amazonaws.com/exposeAPI/getProductHistory?productKey=ELECTROLUX_E6AF1-520K"
const GET_STARBUY_ITEMS = "https://ir39pxdck8.execute-api.us-east-1.amazonaws.com/exposeAPI/getSBProducts"

class ForecastService {
    getCPIForecast() {
        const response = axios.get(CPI_API_URL)
            .then((response) => {
                console.log("Get CPI Forecast Successful")
                return response
            })
            .catch((error) => {
                console.log("Get CPI Forecast NOT successful " + error)
                return error
            })

        return response
    }

    getRSIForecast() {
        const response = axios.get(RSI_API_URL)
            .then((response) => {
                console.log("Get RSI Forecast Successful")
                return response
            })
            .catch((error) => {
                console.log("Get RSI Forecast NOT successful " + error)
                return error
            })

        return response
    }

    getSBCategory() {
        const response = axios.get(SB_API_URL)
            .then((response) => {
                console.log("Get SB Category Successful")
                return response
            })
            .catch((error) => {
                console.log("Get SB Category NOT successful " + error)
                return error
            })

        return response
    }

    getCategoryDemand() {
        const response = axios.get(DD_API_URL)
            .then((response) => {
                console.log("Get Category Demand Successful")
                return response
            })
            .catch((error) => {
                console.log("Get Category Demand NOT successful " + error)
                return error
            })

        return response
    }

    getAllProducts() {
        const response = axios.get(GET_PROD_URL)
            .then((response) => {
                console.log("Get All Products Successful")
                return response
            })
            .catch((error) => {
                console.log("Get All Products NOT successful " + error)
                return error
            })

        return response
    }

    getSingleProd() {
        const response = axios.get(GET_SINGLE_PROD)
            .then((response) => {
                console.log("Get Single Products Successful")
                return response
            })
            .catch((error) => {
                console.log("Get Single Products NOT successful " + error)
                return error
            })

        return response
    }

    getStarbuyItems() {
        const response = axios.get(GET_STARBUY_ITEMS)
            .then((response) => {
                console.log("Get starbuy items forecast Successful")
                return response
            })
            .catch((error) => {
                console.log("Get starbuy items forecast NOT successful " + error)
                return error
            })

        return response
    }

}

export default new ForecastService();
