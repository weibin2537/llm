const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: [
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/dev-server',
    './src/index.js',
  ],
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'bundle.js',
  },
  devServer: {
    hot: true,  // 启用热模块替换
    contentBase: path.join(__dirname, 'public'),
    port: 3000,
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),  // 热模块替换插件
  ],
};
