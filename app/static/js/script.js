const form = document.getElementById("stock-symbol-form");
let intervalId = 0;
form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearInterval(intervalId);
    const formData = new FormData(form);
    const symbol = formData.get("symbol");
    const stockNameElementId = "stock-name";
    const stockPriceElementId = "stock-price";
    const result = await checkStockPrice(symbol, stockNameElementId, stockPriceElementId);
    if (!result) {
        intervalId = setInterval(async (symbol, stockNameElementId, stockPriceElementId) => {
            checkStockPrice(symbol, stockNameElementId, stockPriceElementId);
        }, 500, symbol, stockNameElementId, stockPriceElementId);
    }
});

const checkStockPrice = async (symbol, stockNameElementId, stockPriceElementId) => {
    symbol = encodeURIComponent(symbol);
    let data;
    try {
        data = await d3.json(`https://ts-api.cnbc.com/harmony/app/charts/1D.json?symbol=${symbol}`);
    } catch (error) {
        document.getElementById(stockNameElementId).innerHTML = "Symbol does not exist. Please try again."
        return 1;
    }
    const stockName = `${data.barData.companyName} (${symbol})`;
    const mostRecent = data.barData.priceBars[data.barData.priceBars.length-1];
    const stockPrice = `Open: ${mostRecent.open}, High: ${mostRecent.high}, Low: ${mostRecent.low}, Close: ${mostRecent.close}`;
    document.getElementById(stockNameElementId).innerHTML = stockName;
    document.getElementById(stockPriceElementId).innerHTML = stockPrice;
    return 0;
};
