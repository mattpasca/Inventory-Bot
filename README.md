**--- Inventory Bot ---**

This telegram bot was coded for the owners of a plant nursery in Pistoia.
It's aim is to reduce the waste of time while answering to price requests of customers. In a quote request there are often some articles
that are not available in the nursery and that can be easily found in nearby nurseries. It is common practice to call the colleagues to ask for 
availability and price of the missing plants. This consumes time and can be highly inefficient. In order to achieve a faster response time,
the owners of the nursery go to every colleague before the beginning of the high season to make a broad assessment of the stock of the colleagues. This way, they
already know who to call and in the best case they know already the price and can bypass the call completely.
This bot enables them to create and to update an inventory of the stock of their colleagues remotely with a simple interface (the chat).
The data of each article can be inserted via text or voice messages.

**Commands**
**/start**
Gives a general overview of the bot and some hints about the usage.

<img width="300" alt="image" src="https://github.com/user-attachments/assets/ea9751f1-7cf7-4602-ab40-5adf8cbe0f4e" />

**/c <colleague_name>**
The location of the stock (identified with the name of the colleague) is set globally at the beginning of a session.

<img width="300" alt="image" src="https://github.com/user-attachments/assets/ad5c1413-9e5a-458c-bad3-565eb1316ba6" />

**/n <plant_name>**
It is important to guarantee a maximal level of standardization in all the entries, especially when it comes to the names of the plants. The user can only
select names from a pre existing list. The user input is used to fetch a list of names matched with fuzzy match.
After this command a list of matching plant names is displayed.

<img width="300" alt="image" src="https://github.com/user-attachments/assets/e111564f-7516-4464-931b-7c01ec61d50d" />


**Conversation flow**
(Set colleague name -> ) Search plant -> Insert details (text or voice) -> save / cancel / modify

<img width="300" alt="image" src="https://github.com/user-attachments/assets/475c3b7d-5c24-405b-87bd-be5d336c785f" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/2b04be24-4f76-40aa-9b07-3683c92b573b" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/89978f84-5a8d-44ba-a69e-617acb070fb3" />


The collected data is saved locally on the server machine in a .json that can be easily converted to an Excel table for internal use.
                                                                                            


