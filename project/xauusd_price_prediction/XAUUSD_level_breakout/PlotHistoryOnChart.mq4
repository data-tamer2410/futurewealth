
#property version "1.0"
#property strict

/*

will print myfxbook history onto a chart (or replicate trades in backtester, but disabled right now). 

*/

enum dataFormat {
   MQL5 = 0,          // mql5.com
   MYFXBOOK = 1,      // myfxbook.com
   SIMPLETRADER = 2,  // simpletrader.com
   CUSTOM,            // custom (input variables)
};
extern dataFormat format = MQL5;
extern string d1 = "#------------------------------ Time Settings ------------------------------#";
extern int hourShift = 0;
extern bool myfxbookBrokerUsesDST = true;
extern bool MT4BrokerUsesDST = true;
// the old myfxbook format had month first, but not when I last tested it.
extern bool monthFirstInDate = false;
extern string startDate = "2021.01.01";
extern string d2 = "#------------------------------ File Settings ------------------------------#";
// "statement.csv";
extern string historyFileName = "trade_history_live.csv";
extern string delimiter = ",";
// Open Date,Close Date,Symbol,Action,Units/Lots,SL,TP,Open Price,Close Price,Commission,Swap,Pips,Profit,Gain,Duration (DD:HH:MM:SS),Profitable(%),Profitable(time duration),Drawdown,Risk:Reward,Max(pips),Max(JPY),Min(pips),Min(JPY),Entry Accuracy(%),Exit Accuracy(%),ProfitMissed(pips),ProfitMissed(JPY)
extern string columnOpenDate = "Open Date";
extern string columnCloseDate = "Close Date";
extern string columnSymbol = "Symbol";
extern int symbolCharactersToCheck = 6;
extern string columnOpenPrice = "Open Price";
extern string columnClosePrice = "Close Price";
extern string columnAction = "Action";
extern string actionBuy = "Buy";
extern string actionBuyStop = "Buy Stop";
extern string actionBuyLimit = "Buy Limit";
extern string actionSell = "Sell";
extern string actionSellStop = "Sell Stop";
extern string actionSellLimit = "Sell Limit";
extern string columnLots = "Lots";
extern string d3 = "#------------------------------ Visual Settings ------------------------------#";
extern color colorBuy = clrGreen;
extern color colorBuyStop = clrTurquoise;
extern color colorBuyLimit = clrLimeGreen;
extern color colorSell = clrIndianRed;
extern color colorSellStop = clrMagenta;
extern color colorSellLimit = clrDarkOrange;
extern int lineWidth = 3;

int HOUR = 60*60, MINUTE = 60;

struct TRADE {
   datetime openTime;
   datetime closeTime;
   double openPrice;
   double closePrice;
   double lots;
   bool used;
   ENUM_ORDER_TYPE type;
};

TRADE trades[];

int OnInit() {
   if (format == MQL5) {
      // Time;Type;Volume;Symbol;Price;S/L;T/P;Time;Price;Commission;Swap;Profit;Comment
      delimiter = ";";  // different to myfxbook. 
      columnOpenDate = "Time";  // different to myfxbook. 
      columnCloseDate = "Time";  // different to myfxbook. both the same, therefore using openDateIndexFound.
      columnSymbol = "Symbol";
      symbolCharactersToCheck = 6;
      columnOpenPrice = "Price";  // different to myfxbook. 
      columnClosePrice = "Price";  // different to myfxbook. both the same, therefore using openPriceIndexFound.
      columnAction = "Type";  // different to myfxbook. 
      actionBuy = "Buy";
      actionBuyStop = "Buy Stop";
      actionBuyLimit = "Buy Limit";
      actionSell = "Sell";
      actionSellStop = "Sell Stop";
      actionSellLimit = "Sell Limit";
   } else if (format == MYFXBOOK) {
      monthFirstInDate = false;
      delimiter = ",";
      columnOpenDate = "Open Date";
      columnCloseDate = "Close Date";
      columnSymbol = "Symbol";
      symbolCharactersToCheck = 6;
      columnOpenPrice = "Open Price";
      columnClosePrice = "Close Price";
      columnAction = "Action";
      actionBuy = "Buy";
      actionBuyStop = "Buy Stop";
      actionBuyLimit = "Buy Limit";
      actionSell = "Sell";
      actionSellStop = "Sell Stop";
      actionSellLimit = "Sell Limit";
   } else if (format == SIMPLETRADER) {
      delimiter = "\t";
      columnOpenDate = "Open Time";
      columnCloseDate = "Close Time";
      columnSymbol = "Pair";
      symbolCharactersToCheck = 6;
      columnOpenPrice = "Open Price";
      columnClosePrice = "Close Price";
      columnAction = "Type";
      actionBuy = "Buy";
      actionBuyStop = "Buy Stop";
      actionBuyLimit = "Buy Limit";
      actionSell = "Sell";
      actionSellStop = "Sell Stop";
      actionSellLimit = "Sell Limit";
   }


   if (IsTesting()) return INIT_SUCCEEDED;
   int handle = FileOpen(historyFileName, FILE_TXT|FILE_READ);
   Print("handle: ", handle, " | historyFileName: ", historyFileName);
   bool firstLine = true;
   int tradeIndex = 0, maxIndex = 0, symbolIndex = 0, actionIndex = 0;
   int openDateIndex = 0, closeDateIndex = 0, openPriceIndex = 0, closePriceIndex = 0, columnLotsIndex = 0;
   while(!FileIsEnding(handle)) {
      string line = FileReadString(handle);
      // Print("line: ", line);
      string data[];
      ushort uSep = StringGetCharacter(delimiter, 0);
      int k = StringSplit(line, uSep, data);
      if (firstLine) {
         firstLine = false;
         bool openDateIndexFound = false;
         bool openPriceIndexFound = false;
         for (int i=0; i<ArraySize(data); i++) {
            if (StringFind(data[i], columnOpenDate) != -1 && !openDateIndexFound) {
               openDateIndexFound = true;
               openDateIndex = i;
            }
            if (StringFind(data[i], columnCloseDate) != -1) closeDateIndex = i;
            if (StringFind(data[i], columnSymbol) != -1) symbolIndex = i;
            if (StringFind(data[i], columnAction) != -1) actionIndex = i;
            if (StringFind(data[i], columnOpenPrice) != -1 && !openPriceIndexFound) {
               openPriceIndexFound = true;
               openPriceIndex = i;
            }
            if (StringFind(data[i], columnClosePrice) != -1) closePriceIndex = i;
            if (StringFind(data[i], columnLots) != -1) columnLotsIndex = i;
         }
         Print("Column for open date: ", openDateIndex, " | close date: ", closeDateIndex, " | symbol: ", symbolIndex, " | action: ", actionIndex, " | open price: ", openPriceIndex, " | close price: ", closePriceIndex);
         maxIndex = MathMax(MathMax(MathMax(MathMax(MathMax(openDateIndex, closeDateIndex), openPriceIndex), closePriceIndex), symbolIndex), actionIndex);
         continue;
      }
      if (ArraySize(data) < maxIndex+1) continue;
      string symbol = data[symbolIndex];
      if (StringFind(StringSubstr(Symbol(), 0, symbolCharactersToCheck), StringSubstr(symbol, 0, symbolCharactersToCheck)) == -1) continue;
      ENUM_ORDER_TYPE type = -1;
      if (StringCompare(data[actionIndex], actionBuy) == 0) type = OP_BUY;
      else if (StringCompare(data[actionIndex], actionBuyLimit) == 0) type = OP_BUYLIMIT;
      else if (StringCompare(data[actionIndex], actionBuyStop) == 0) type = OP_BUYSTOP;
      else if (StringCompare(data[actionIndex], actionSell) == 0) type = OP_SELL;
      else if (StringCompare(data[actionIndex], actionSellLimit) == 0) type = OP_SELLLIMIT;
      else if (StringCompare(data[actionIndex], actionSellStop) == 0) type = OP_SELLSTOP;
      string openDateStr = data[openDateIndex];
      // Print(openDateStr);
      string closeDateStr = data[closeDateIndex];
      if (format != MQL5) {
         string day = StringSubstr(openDateStr, 0, 2);
         string month = StringSubstr(openDateStr, 3, 2);
         if (monthFirstInDate) {
            day = StringSubstr(openDateStr, 3, 2);
            month = StringSubstr(openDateStr, 0, 2);
         }
         string year = StringSubstr(openDateStr, 6, 4);
         string time = StringSubstr(openDateStr, 10, 6);
         openDateStr = year + "." + month + "." + day + time;
         day = StringSubstr(closeDateStr, 0, 2);
         month = StringSubstr(closeDateStr, 3, 2);
          if (monthFirstInDate) {
            day = StringSubstr(closeDateStr, 3, 2);
            month = StringSubstr(closeDateStr, 0, 2);
         }
         year = StringSubstr(closeDateStr, 6, 4);
         time = StringSubstr(closeDateStr, 10, 6);
         closeDateStr = year + "." + month + "." + day + time;
      }
      // Print("1: ", openDateStr);
      datetime openTime = StrToTime(openDateStr);
      // Print(openTime);
      openTime += (hourShift + DSToffset(openTime)) * HOUR;
      // Print(openTime);
      // string arr[] = {};
      // Print(arr[0]);
      if (StringLen(startDate) > 0 && openTime < StringToTime(startDate + " 00:00")) continue;  // to reduce the number. 
      // if (IsTesting() && openTime < TimeCurrent()) continue;
      datetime closeTime = StrToTime(closeDateStr);
      closeTime += (hourShift + DSToffset(openTime)) * HOUR;
      StringReplace(data[openPriceIndex], " ", "");  // thousands separator can be "3 351.35". maybe also remove commas?
      StringReplace(data[closePriceIndex], " ", "");
      double openPrice = StringToDouble(data[openPriceIndex]);
      if (openPrice == 0) continue;
      double closePrice = StringToDouble(data[closePriceIndex]);
      if (closePrice == 0) closePrice = openPrice;  // might be the case for pending orders. 
      // if (type != OP_BUYLIMIT) continue;
      double lots = StringToDouble(data[columnLotsIndex]);
      // 2023.10.06 07:48:38.053	MyfxbookHistoryToChart_v1.0 USDJPY,H1: line: 28/09/2023 00:56,28/09/2023 01:56,USDJPY,Buy,0.300,149.36000,149.72200,149.52000,149.46400,0.0000,0.0000,-5.6,-1680.00,-0.14,00:01:00:07,0.0,0s,7.5,7.50,0.0,0.0,-7.5,-2250.0,0.0,25.3,-5.60,-1680.00
      Print(openDateStr, " | ", openTime, " | ", closeTime, " | ", typeString(type), " | ", lots, " | ", DoubleToString(openPrice, Digits), " | ", DoubleToString(closePrice, Digits));
      // return INIT_SUCCEEDED;
      ArrayResize(trades, tradeIndex+1);
      trades[tradeIndex].openTime = openTime;
      trades[tradeIndex].closeTime = closeTime;
      trades[tradeIndex].openPrice = openPrice;
      trades[tradeIndex].closePrice = closePrice;
      trades[tradeIndex].type = type;
      trades[tradeIndex].lots = lots;
      trades[tradeIndex].used = false;
      tradeIndex++;
   }
   FileClose(handle);
   if (IsTesting()) return INIT_SUCCEEDED;
   drawAllLines();
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
   ObjectsDeleteAll();
   // drawAllLines();  // for backtest version. 
}

/*
void OnTick() {
   return;
   if (!replicateTrades) return;
   for (int i=0; i<ArraySize(trades); i++) {
      if (!trades[i].used && TimeCurrent() >= trades[i].openTime) {
         trades[i].used = true;
         string orderComment = IntegerToString(i);
         // to check if there is a filter for the last X candles to have the same direction. but did not look like it. still it is usually waiting a few candles. 
         if (TimeCurrent() > lastTradeTime + 12 * HOUR) {
            lastTradeTime = TimeCurrent();
            Print((int)(Close[1]>Close[2]), " | ", (int)(Close[2]>Close[3]), " | ", (int)(Close[3]>Close[4]), " | ", (int)(Close[4]>Close[5]), " | ", (int)(Close[5]>Close[6]), " | ", (int)(Close[6]>Close[7]), " | ");
         }
         if (trades[i].direction == 1) bool res = OrderSend(Symbol(), OP_BUY, lots, Ask, slippagePoints, 0, 0, orderComment, magic, 0, Blue);
         else if (trades[i].direction == -1) bool res = OrderSend(Symbol(), OP_SELL, lots, Bid, slippagePoints, 0, 0, orderComment, magic, 0, Red);
      }
   }
   for (int i=OrdersTotal()-1; i >=0; i--) {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      for (int j=0; j<ArraySize(trades); j++) {
         // Print(j, " | ", OrderComment(), " | ", TimeCurrent() >= trades[j].closeTime, " | ", trades[j].closeTime);
         if (StringFind(OrderComment(), IntegerToString(j)) != -1 && TimeCurrent() >= trades[j].closeTime) {
            bool res = OrderClose(OrderTicket(), OrderLots(), Bid, slippagePoints, Yellow);
         }
      }
   }
}
*/

int DSToffset(datetime time) {
   if (myfxbookBrokerUsesDST && !MT4BrokerUsesDST && isSummerTimeNY(time)) return -1;
   if (!myfxbookBrokerUsesDST && MT4BrokerUsesDST && isSummerTimeNY(time)) return 1;
   return 0;
}

// explained here:
// http://delphiforfun.org/programs/math_topics/dstcalc.htm
// http://www.webexhibits.org/daylightsaving/i.html
bool isSummerTimeNY(datetime time) {
   int year = TimeYear(time);
   int month = TimeMonth(time);
   int day = TimeDay(time);
   // the US will permanently use summer time. but not sure from what date exactly. probably after the shift in 2023. 
   // we would have to rename all "winter" settings since there will only be summer offset. 
   // if (year >= 2024 || (year == 2023 && month >= 4)) return true;
   if (year >= 2007) {
      int marchDSTday = 14 - (int)MathMod((1 + (5*year)/4), 7);   // second Sunday in March
      int novemberDSTday = 7 - (int)MathMod((1 + (5*year)/4), 7); // first Sunday in November
      return (month > 3 && month < 11) || (month == 3 && day >= marchDSTday) || (month == 11 && day < novemberDSTday);
   } else if (year >= 1987 && year <= 2006) {
      int aprilDSTday = 1 + (int)MathMod((2 + 6*year - year/4), 7); // first Sunday in April
      int octoberDSTday = 31 - (int)MathMod((1 + (5*year)/4), 7);   // last Sunday in October
      return (month > 4 && month < 10) || (month == 4 && day >= aprilDSTday) || (month == 10 && day < octoberDSTday);
   }
   return month > 3 && month < 11;
}


string typeString(ENUM_ORDER_TYPE type) {
   if (type == OP_BUY) return "Buy";
   else if (type == OP_BUYSTOP) return "Buy Stop";
   else if (type == OP_BUYLIMIT) return "Buy Limit";
   else if (type == OP_SELL) return "Sell";
   else if (type == OP_SELLSTOP) return "Sell Stop";
   else if (type == OP_SELLLIMIT) return "Sell Limit";
   else return "none";
}

void drawAllLines() {
   for (int i=0; i<ArraySize(trades); i++) {
      bool isPendingOrder = trades[i].type == OP_BUYLIMIT || trades[i].type == OP_BUYSTOP || trades[i].type == OP_SELLLIMIT || trades[i].type == OP_SELLSTOP;
      // if (!drawLinesForPendingOrders && isPendingOrder) continue;
      color col = clrGray;
      if (trades[i].type == OP_BUY) col = colorBuy;
      else if (trades[i].type == OP_BUYSTOP) col = colorBuyStop;
      else if (trades[i].type == OP_BUYLIMIT) col = colorBuyLimit;
      else if (trades[i].type == OP_SELL) col = colorSell;
      else if (trades[i].type == OP_SELLSTOP) col = colorSellStop;
      else if (trades[i].type == OP_SELLLIMIT) col = colorSellLimit;
      else continue;
      if (!isPendingOrder) {
         // to draw one line representing the trade: 
         drawTrendLine(0, "line"+IntegerToString(i)+"_"+DoubleToString(trades[i].lots, 2), 0, trades[i].openTime, trades[i].openPrice, trades[i].closeTime, trades[i].closePrice, col, lineWidth);
      } else {
         // to just draw one line at the open price from openTime to closeTime.
         drawTrendLine(0, "linePending"+IntegerToString(i)+"_"+DoubleToString(trades[i].lots, 2), 0, trades[i].openTime, trades[i].openPrice, trades[i].closeTime, trades[i].openPrice, col, lineWidth);
         // to draw two lines at entry and exit:
         // drawTrendLine(0, "lineEntry"+IntegerToString(i), 0, trades[i].openTime, trades[i].openPrice, trades[i].openTime+PeriodSeconds(PERIOD_CURRENT), trades[i].openPrice, col, lineWidth);
         // drawTrendLine(0, "lineClose"+IntegerToString(i), 0, trades[i].closeTime, trades[i].closePrice, trades[i].closeTime+PeriodSeconds(PERIOD_CURRENT), trades[i].closePrice, col, lineWidth);
      }
   }
   drawText("fileName", CORNER_LEFT_UPPER, 23, 23, clrWhite, "History file: " + historyFileName);
}

void drawText(string name, int corner, int x, int y, color col, string text) {
   ObjectCreate(name, OBJ_LABEL, 0, 0, 0);
   ObjectSetText(name, text, 13, "Verdana", col);
   ObjectSet(name, OBJPROP_CORNER, corner);
   ObjectSet(name, OBJPROP_XDISTANCE, x);
   ObjectSet(name, OBJPROP_YDISTANCE, y);
   ObjectSet(name, OBJPROP_BACK, false);
}

bool drawTrendLine(const long            chart_ID=0,        // chart's ID
                 const string          name="TrendLine",  // line name
                 const int             sub_window=0,      // subwindow index
                 datetime              time1=0,           // first point time
                 double                price1=0,          // first point price
                 datetime              time2=0,           // second point time
                 double                price2=0,          // second point price
                 const color           clr=clrRed,        // line color
                 const int             width=1,           // line width
                 const ENUM_LINE_STYLE style=STYLE_SOLID, // line style
                 const bool            back=false,        // in the background
                 const bool            selection=false,    // highlight to move
                 const bool            ray_right=false,   // line's continuation to the right
                 const bool            hidden=true,       // hidden in the object list
                 const long            z_order=0)         // priority for mouse click
  {
//--- set anchor points' coordinates if they are not set
   // ChangeTrendEmptyPoints(time1,price1,time2,price2);
//--- reset the error value
   ResetLastError();
//--- create a trend line by the given coordinates
   if(!ObjectCreate(chart_ID,name,OBJ_TREND,sub_window,time1,price1,time2,price2)) {
   //   Print(__FUNCTION__,
   //         ": failed to create a trend line! Error code = ",GetLastError());
   //   return(false);
   }
//--- set line color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set line display style
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set line width
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the line by mouse
//--- when creating a graphical object using ObjectCreate function, the object cannot be
//--- highlighted and moved by default. Inside this method, selection parameter
//--- is true by default making it possible to highlight and move the object
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTED,selection);
//--- enable (true) or disable (false) the mode of continuation of the line's display to the right
   ObjectSetInteger(chart_ID,name,OBJPROP_RAY_RIGHT,ray_right);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//--- successful execution
   return(true);
}