Odoo 11.0 Enterprise Edition

Installation 
============
* Install the Application => Apps -> Sale Helpdesk Extend (Technical Name: sale_helpdesk_extend)

Feature
=======
* Using this module in helpdesk if we select the customer it will display the records in list who belongs to that customer and Is Sat field is set to true.A new field is added in helpdesk ticket stage if it is true then only mail functionality will run.A button is added in Helpdesk ticket form and on click of that wizard for mail will be opened and clicking send button mail will be sent.

* In Sales Quotation Line after setting product price if we update quantity it will not change updated price and discount in quotation line. Out of box functionality of updating price and discount on change of quantity has been stopped.

Note: We have not display Email address of contacts as if email is long then view will get changed.

Fixes as on 13.11.2018 - version 11.0.1.0.1
--------------------------------------------

* Fixed the Subject issue in Helpdesk Email.


Features Added on 13.03.2019 - version 11.0.1.1.0
---------------------------------------------------
* Added "customer" in list view of Manufacturing Orders.
->After generate "Manufacturing Order" from Sale Order you can see customer name is added in that "Manufacturing Order".
* Added "total_time" in list view of Tickets.
* After selecting records for menu "Helpdesk"-> All Tickets" and click "Calculate Average Time" -> "Calculate",
  it will calculate "Average Time" for all Tickets and calculated "Average Time" will displyed in pivot view.


Features Added/Removed on 04.04.2019 - version 11.0.1.2.0
---------------------------------------------------------
* Added calculation of "Total Spent Time" from timesheet.
* Added fields to partner for calculate "Average Time".
* Added calculation of "Average Time".
* Removed past calculation of "Average Time" which comes from wizard.
* Added wizard for printing Helpdesk Ticket Report.
* Added Functionality of PDF and XLS report printing.
* Added "Salesperson" directly from Customer.
* Remove automatically added Customer from Follower.
* Added Salesperson to Follower.

Features Added/Removed on 04.04.2019 - version 11.0.1.2.1
---------------------------------------------------------
* Fixed folloer not add using automated actions.

Features Added/Removed on 16.04.2019 - version 11.0.1.2.2
---------------------------------------------------------
* Fixed access error for sales user.
* Added groups for Total spent hours field in res.partner for Helpdesk users.

Features Added/Removed on 16.04.2019 - version 11.0.1.2.4
---------------------------------------------------------
* Changes made by Victor

Features Added/Removed on 16.04.2019 - version 11.0.1.2.5
---------------------------------------------------------
* Added brief page with ticket details as per SOW 5

Features Added/Removed on 16.04.2019 - version 11.0.1.2.6
---------------------------------------------------------
* Fixed issue related to unique subtype.

Features Added/Removed on 26.07.2019 - version 11.0.1.2.7
---------------------------------------------------------
* Added table on top as per SOW6

Features Added on 06.11.2019 - version 11.0.1.3.0
---------------------------------------------------------
* Added domain in Customer field to display only companies record.
* Added domain in Client Customer field to display only selected Customer related contacts.
* Added domain rules to set Task values based on below condition:
    > Selected task which has lower sequence of stages. If more than 1 Task in stage with lower sequence number then task with lower seuquence is selected.

Features Added on 06.11.2019 - version 11.0.1.3.3
---------------------------------------------------------
* Updated and improve filter code based on stage and then task.

Fixed issue on 29.Feb.2020 - version 11.0.1.3.4
---------------------------------------------------------
* Fixed issue of write method and not update task based on child contacts.

Features Added on 03.03.2020 - version 11.0.1.3.5
---------------------------------------------------------
* Added Filter and Groupby on account analytic line view

VTB Features Added on 05.03.2020 - version 11.0.1.3.6
---------------------------------------------------------
* Added new field policetype on res.partner model and views

Fixed Issues on 07.03.2020 - version 11.0.1.3.7
-----------------------------------------------
* Added "contacts" in depends.
* Added access rights for the new object "police.type".


Fixed Issues on 13.03.2020 - version 11.0.1.3.8
-----------------------------------------------
* Changed police type field type from many2mnany to many2one.


Added feature on 21.03.2020 - version 11.0.1.4.0
-------------------------------------------------
* Added a clickable field stage in form,tree.
* Added by group by stage in kanban view.
* Added a functionality that if the project is created from the sale order then its name should be like SO Number + Customer Reference.

Added feature on 25.03.2020 - version 11.0.1.4.1
-------------------------------------------------
* Added default group by on project dashboard.
* Changed key values for field stage.
* Added a translation file.

VTB Added feature on 20.04.2020 - version 11.0.1.4.2
-------------------------------------------------
* Added new fields region One2Many and Is Invoicing Boolean on res.partner

Added features on 04.05.2020 - version 11.0.1.5.2
-------------------------------------------------
* On helpdesk report ticket, filter totals tables based on customer selection.
* Modify section Header report: Added VAT field after company details.
* Update Sales Order & Invoice Body section report:
* Footer section report: Reduced font size text for report_footer field to 9px

VTB Added feature on 05.05.2020 - version 11.0.1.5.3
-------------------------------------------------
* On project.task model add sale_order_id many2one and show it in form and tree views

Added features on 18.05.2020 - version 11.0.1.6.3
-------------------------------------------------
* Add terms & consitions in purchase report
* Remove "Taxes" and "Purchase Request Date" from the purchase report
* Reduce font size of purchase report to 12px