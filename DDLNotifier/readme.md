### GPT Prompt
我有一个需求，帮我写一个python脚本，利用beautiful soup能够监控
特定URL当中的特定内容的变化。
我的想法是首先每次运行这个python脚本，下载原html；以及一个项目名称 - ddl的表格，
然后和之前下载表格的内容进行比较，
关注每一个特定要求的项目的ddl的变化。如果有变化就发送邮件给特定的邮箱。

URL为
URL = 'https://www.gs.cuhk.edu.hk/admissions/admissions/application-deadline'

要求
只需要关注 Taught Programmes 这一列，这样的话
你应该需要关注的只有<div class="_50 application-deadline-tb-col content-tb right">里面
的项目的ddl变化，参考我给你的图片。
参考HTML格式：
<div class="faqs-answer _on">
            <div class="application-deadline-answer-box">
              <div data-ix="scroll-fadein-from-bottom" class="application-deadline-tb-row content-tb w-clearfix">
                <div class="_50 application-deadline-tb-col content-tb">
                  <div class="application-deadline-tb-txt title">Research Programmes<span class="color-lightblue"></span></div>
                </div>
                <div class="_50 application-deadline-tb-col content-tb right">
                  <div class="application-deadline-tb-txt title">Taught Programmes<span class="color-lightblue"></span></div>
                </div>
              </div>
              <div data-ix="scroll-fadein-from-bottom" class="application-deadline-tb-row content-tb w-clearfix">
                <div class="_50 application-deadline-tb-col content-tb">
                                                      <div class="application-deadline-tb-txt">
                    MPhil in Anthropology                    <div class="color-lightblue"><p>Main Round: 1 December 2023<br /> Clearing Round: 31 March 2024<br /> (Applications in Clearing Round will only be considered subject to availability of places.)</p></div>
                  </div>
                                    <div class="application-deadline-tb-txt">
                    PhD in Anthropology                    <div class="color-lightblue"><p>Main Round: 1 December 2023<br /> Clearing Round: 31 March 2024<br /> (Applications in Clearing Round will only be considered subject to availability of places.)</p></div>
                  </div>
                                                    </div>
                <div class="_50 application-deadline-tb-col content-tb right">
                                                          <div class="application-deadline-tb-txt">
                      MA in Anthropology                      <table class="application_deadline_table" width="100%">
                                                <tr>
                          <td>
                            <div class="color-lightblue"><p>1st round: 30 September 2023</p>
<p>2nd round: 31 October 2023</p>
<p>3rd round: 30 November 2023</p>
<p>4th round: 31 December 2023</p>
<p>5th round: 31 January 2024</p>
<p style="text-align:justify;">Applications will be processed on a rolling basis from October 2023 until all places have been filled. Therefore, early applications are strongly encouraged. Applications submitted after 31 December 2023 may be considered, subject to availability of places.</p></div>
                          </td>
                                                  </tr>
                      </table>
                    </div>
                                                      </div>
              </div>
            </div>
          </div>
        </div>

参考另一个与改格式不同的类似功能的代码：

# Constants
URL = 'https://admissions.hku.hk/tpg/programme-list'
SAVE_PATH_HTML = 'previous_page.html'  # Save path for the HTML
SAVE_PATH_CSV = 'programme_data.csv'  # Save path for the CSV
recipient_email = 'yamy12344@gmail.com'


def download_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all tables with the specified class attributes
    tables = soup.find_all('table', {'class': 'table table-bordered table-striped'})

    programme_data = []

    for table in tables:
        rows = table.find_all('tr')

        # Extracting headers from the first table only, assuming all tables have the same structure
        headers = ["Programme", "Deadline", "Apply"]
        if not programme_data:
            headers = [header.get_text().strip() for header in rows[0].find_all('th')]
            headers = headers[:1] + headers[2:4]  # Adjusting the headers to exclude the 'Download Documents' column

        # Extracting rows
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:  # Ensure there are enough columns
                programme_name = cols[0].get_text().strip()
                deadline_info = cols[2].get_text().strip()
                apply_info = cols[3].get_text().strip()

                # Check for full-time option
                if 'Full Time' in apply_info:
                    programme_data.append([programme_name, deadline_info, apply_info])

    return pd.DataFrame(programme_data, columns=headers)


def compare_and_notify(old_data, new_data):
    # Assuming the 'Programme' column has unique values that can be used as an identifier
    if not old_data.equals(new_data):
        print("Data differences detected...")

        # Identifying changes between old and new data
        changes_detected = []
        for programme in new_data['Programme'].unique():
            old_row = old_data[old_data['Programme'] == programme]
            new_row = new_data[new_data['Programme'] == programme]

            # If there's a change in the 'Deadline' column for a 'Full Time' programme
            if not old_row.equals(new_row) and 'Full Time' in new_row['Apply'].values[0]:
                old_deadline = old_row['Deadline'].values[0] if not old_row.empty else 'N/A'
                new_deadline = new_row['Deadline'].values[0] if not new_row.empty else 'N/A'
                changes_detected.append({
                    'Programme': programme,
                    'Old Deadline': old_deadline,
                    'New Deadline': new_deadline
                })

        # Sending a consolidated email if changes were detected
        if changes_detected:
            subject = "Changes Detected in Programmes"
            body = "The following changes have been detected:\n\n"
            for change in changes_detected:
                body += (f"Programme: {change['Programme']}\n"
                         f"Old Deadline: {change['Old Deadline']}\n"
                         f"New Deadline: {change['New Deadline']}\n\n")

            send_email(subject, body, recipient_email)
            print("Email notification sent for the detected changes.")
        else:
            print("No changes detected in the data table with 'Full Time' in Apply column.")
    else:
        print("No changes detected in the data content.")

def main():
    # Download HTML
    new_html = download_html(URL)
    
    # Parse new HTML to get data
    new_data = parse_html(new_html)

    # Read old data if it exists
    if os.path.exists(SAVE_PATH_CSV):
        old_data = pd.read_csv(SAVE_PATH_CSV)
    else:
        old_data = pd.DataFrame()

    # Compare and notify
    compare_and_notify(old_data, new_data)

    new_data.to_csv(SAVE_PATH_CSV, index=False)
