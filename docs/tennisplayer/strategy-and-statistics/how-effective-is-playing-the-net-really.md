---
title: "How Effective Is Playing the Net Really?"
section: "Strategy and Statistics"
source: "tennisplayer.net archive"
language: en
---



### Jeremy Rosen

------------------------------------------------------------------------



**How statistically effective is playing the net really?**

Is playing the net more effective than staying at the baseline? The simplest method to answer this question is to compare win probabilities at the net versus at the baseline.

In the final section of his brilliant article on the New Magic Numbers, Craig O\'Shannessy reports that players won 65% of their approaches in his studies at the U.S. Open, and that this percentage was almost as high at every level, from 12 and unders up through college tennis. ([Click Here](https://www.tennisplayer.net/members/strategy/jeremy_rosen/craig_o_shannessy/the_new_magic_numbers/).)

However, my research shows this method is insufficient to make a truly accurate determination. Why? Because win probabilities at net can be deceptively high.

When using statistics to determine the effectiveness of playing the net, it\'s essential to account for other relevant variables\--not just win probabilities. For instance, many approach shots are hit off easy balls, which give you an advantage in winning the point irrespective of whether you approach the net or not.

Suppose you serve four points. Twice, the returner floats the return, and you approach the net and put away easy volleys. But the other two points, the returner hammers the return and forces you to play defense.

You lose one of those two points, but you grind out the other one. The result is you end up with a 100% win probability at net and a 50% win probability at the baseline. On the surface, that suggests that playing the net was more effective than staying back.



**What do the raw numbers on approaches really mean?**

But in the case of the two floating returns, the act of playing the net was not necessarily in and of itself the reason for your higher win probability. In fact, had you stayed back on all four points, you probably would have still won three of them because of the floated returns.

And if you had come to net on the two points following a strong return, you probably would have lost both of them due to the lack of an opportunity to hit a quality approach shot. So in our hypothetical example, coming to net more often would not have helped you win more points and may have even cost you one or both of the points you won at the baseline.

The point is there are variables other than simply approaching the net that affect win probabilities. In our example, whether the hypothetical returner floated or hammered the return.

**Confounders**

I call these variables Confounders. My research shows it\'s impossible to analyze the impact of playing the net separately from the impact of Confounders.

So how do you really assess the effectiveness of going to the net? Through a statistical technique called Regression Analysis. Using Regression Analysis I can account for the Confounders and quantify the true impact of playing the net more accurately.



**The return is short and centered, so Rafael Nadal approaches the net and puts away a volley.**

To demonstrate how Regression Analysis works, I analyzed the 2016 Wimbledon men\'s final, in which Andy Murray defeated Milos Raonic 6-4, 7-6, 7-6. Just one match played a surface conducive to net play, but the results are suggestive and I believe would be widely confirmed by additional analysis.

What I found was that the characteristics of each incoming ball hit to the player by the opponent affected the players\' win probabilities. To show this I treated every shot\--rather than every point\--as a separate event.

Excluding the serve and return, I looked at every rally shot in which both players were on the baseline. For purposes of simplicity, I also excluded serve and volley points which are a separate category with its own set of complex variables.

In looking only at the baseline points, I considered 5 variables.

1.  **Who won the point.**

2.  **Whether there was an approach.**

3.  **Whether the incoming ball was short landing inside the service line.**

4.  **Whether the incoming ball landed in the center of the court.**

5.  **And whether the incoming ball was defensive, meaning floated or lobbed.**

The results are in Table 1. Win in the table means the player ultimately wins the point. Approach defines whether the player hit an approach shot. Short means the incoming ball landed inside the service line. Centered means the incoming ball landed in the middle third of the court. Defensive means the incoming ball was floated or lobbed.

In my analysis, these 4 variables\--Approach, Short, Centered, and Defensive\--are all independent variables. Win is the dependent variable. For the purposes of assessing the effectiveness of net play, Approach is the independent variable of interest. The other 3 independent variables are the Confounders.



**Players can win points on Confounders on groundstrokes as well as on volleys.**

Intuitively we know, pros often approach the net on short, centered, or defensive balls. But they often win the point on these balls regardless of whether they approach the net or not. So not accounting for these Confounders may make approaching seem more effective than it actually is.

This is because winning the point on a Confounder can happen either at the net or on a groundstroke. Therefore the act of going to net in and of itself is not the necessary reason a player wins the point. It\'s more a matter of the incoming ball.

Let\'s see how this played out in the Wimbledon final between Murray and Raoinc. Let\'s look at total points won in baseline rallies, again excluding serve and return.

Murray won104 of these baseline points and lost 81. Raonic won 98 but lost 108. Murray approached on 17 of these baseline points. Raonic approached much more often, as you would expect from him, coming in off baseline rallies 51 times. The results are shown below in Table 1.

**Table 1: Number of Shots per Category**

  -------------------------------------------
        ** **       **Murray**   **Raonic**
  ----------------- ------------ ------------
        ** **       104          98

       **WIN**      (56%)        (48%)

                    81           108

      **LOSE**      (44%)        (52%)

    **APPROACH**    17 (9%)      51 (25%)

                    168          155

    **STAY BACK**   (91%)        (75%)

                    38           38

      **SHORT**     (21%)        (18%)

                    147          168

    **NOT SHORT**   (79%)        (82%)

                    85           76

    **CENTERED**    (46%)        (37%)

       **NOT**      100          130

    **CENTERED**    (54%)        (63%)

                                 21

    **DEFENSIVE**   11 (6%)      (10%)

       **NOT**      174          185

    **DEFENSIVE**   (94%)        (90%)

   **Total Shots**  **185**      **206**

        ** **       ** **        ** **
  -------------------------------------------

For each player, my goal was to compare the apparent impact of these approaches on who won the point. First when I don\'t account for the Confounders, and then when I do. If the impact of the approaches is more positive when I don\'t account for the Confounders and less positive when I do, then the Confounders are inflating the win probability associated with approaching.

To find out the answer, I run what are called Regressions with and without the Confounders for each player. In these Regressions, each independent variable has its own estimated impact on the dependent variable\--who won the point.



**I found that Confounders inflated the win probability associated with approaching.**

Quantifying the success of approaches without accounting for the Confounders is the same as calculating raw win probabilities the way Craig O\'Shannessy does. But the Regressions account for the effect of the Confounders, that is, the balls that were short, centered or defensive.

In Table 2, I present the results of all four Regressions; each Regression is in its own column. The first two regressions are for Murray, and the last two are for Raonic.

For each player, the regression titled No Confounders lacks the Confounders, whereas the one titled Confounders contains them. Also, for each Regression, each number in the table quantifies the impact of the corresponding variable on Win. As a hypothetical example, if the number corresponding to the variable Approach is 25.0%, then approaching is 25.0% more effective than staying back.

Finally, all four Regressions contain a term called Constant. In the Regressions without the Confounders, Constant is the player\'s win probability when he stays back. To calculate his win probability when he approaches, just add Approach and Constant.

Now the Regressions with Confounders. Constant is still the player\'s win probability when he stays back and the incoming ball is neither short nor centered nor defensive.

To find his win probability when he approaches, and the incoming ball is short but not centered or defensive add Constant, Approach and Short.And the same for the other Confounders/ For more on the math of all this, check out the analysis on my website. ([Click Here](https://www.topspinshotresearch.com/).)

**Table 2: Win Probability Regressions**

+--------------+------------------------------+------------------------------+
|              | Murray (185 Shots)           | Raonic (206 Shots)           |
+==============+================+=============+================+=============+
|              | No Confounders | Confounders | No Confounders | Confounders |
+--------------+----------------+-------------+----------------+-------------+
| **CONSTANT** | 53.0%          | 45.0%       | 41.9%          | 39.4%       |
+--------------+----------------+-------------+----------------+-------------+
| **APPROACH** | 35.3%          | 22.2%       | 22.8%          | 16.4%       |
+--------------+----------------+-------------+----------------+-------------+
| **SHORT**    |                | 5.9%        |                | 6.9%        |
+--------------+----------------+-------------+----------------+-------------+
| **CENTERED** |                | 16.3%       |                | 5.0%        |
+--------------+----------------+-------------+----------------+-------------+
| **DEFENSVE** |                | 8.7%        |                | 10.3%       |
+--------------+----------------+-------------+----------------+-------------+
|              |                |             |                |             |
+--------------+----------------+-------------+----------------+-------------+

What did I find? Per Table 2, without accounting for the Confounders, Murray\'s raw win probability was 35.3% higher when approaching the net than when staying back. His raw win probabilities were 53.0% when staying back and 88.3% when approaching However, when I account for the Confounders, it turns out that approaching benefited him by only 22.2%. So not accounting for Confounders did deceptively inflate his win probability when approaching.



**The depth of Nadal\'s slice backhand makes the subsequent approach less effective, resulting in a passing shot.**

In comparison, Raonic\'s raw win probability was 22.8% higher when approaching than when staying back, 41.9% when staying back and 64.7% when approaching. When accounting for the Confounders, approaching was only 16.4% more effective than staying back. So the true benefit of approaching for Raonic was closer to 16.4% than 22.8%.

**Conclusion**

In summary, while Murray and Raonic were generally both better off when approaching, failing to account for the Confounders makes approaching seem more effective than it actually was. Without Regression Analysis, it wouldn\'t be possible to draw this conclusion.

In this match all 17 of Murray\'s approaches had one or more Confounders. Of Raonic\'s 51 approaches, 46 were the same---one or more Confounders. Interestingly, though not statistically significant, of Raonic\'s 6 approaches without a Confounder he won 2 points and lost 4.

No doubt playing the net can be an effective tactic. Despite the Confounders making approaching seem more effective, approaching still had a positive impact for both Murray and Raonic.

But, as noted, this was just one match, and one played on grass. So obviously a lot more data would be necessary to analyze the overall effectiveness of net play on the Tour or at other levels. In fact, there may be players who have high win probabilities at net but should approach less often than they do.

But Regression Analysis is useful for analyzing more than just approaches. It can help quantify the effectiveness of any tactic subject to Confounders. I\'ve found in other match analyses that some offensive tactics also have deceptively high win probabilities. Swinging volleys, for one, are often winners since they\'re hit off floaters and/or close to the net. But that doesn\'t necessarily mean you should swing at a greater percentage of your volleys.

Lastly, regression analysis is useful for analyzing more than just playing the net. That is, it can help quantify the effectiveness of any tactic subject to confounders.

For instance, I\'ve found in other match analyses that offensive tactics generally have deceptively high win probabilities. Relative to traditional volleys, swinging volleys, for one, are often winners since they\'re hit off floaters. But that doesn\'t mean you should swing at a greater percentage of your volleys.

In contrast, defensive tactics, such as slice lobs, tend to have deceptively low win probabilities. But just because slice lobs don\'t usually win you the point doesn\'t mean you shouldn\'t hit them when you don\'t have better options. Ultimately, with more data and careful interpretation of that data, pros and all players could better understand which tactics are most effective for their game.

+-------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|  | Jeremy Rosen is a former college tennis player and math major who runs a tennis analytics website called Topspin Shot Research. ([Click Here](https://www.topspinshotresearch.com/).) He uses advanced statistical techniques to better contextualize traditional tennis statistics. He also conducts sports economics research for tennis, football, and baseball that have been published in Contemporary Economic Policy, Georgetown Center for Economic Research Working Papers, Football Outsiders, and Baseball Prospectus. |
|                                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|                                                                                                                                                 | He is currently co-authoring a paper with Georgetown University economics professors that uses dynamic game theory to uncover suboptimal serving strategies in the ATP and WTA.                                                                                                                                                                                                                                                                                                                                                   |
+=================================================================================================================================================+===================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+
