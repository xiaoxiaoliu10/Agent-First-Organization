import re
import logging
import requests


logger = logging.getLogger(__name__)

class Pipeline():
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    

class BaseBot():
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def clean_error_url(self, text):
        '''Corrects URLs that are missing the 'h' in 'http://' or 'https://' '''
        # Pattern to find 'ttp://' or 'ttps://' not preceded by 'h'
        pattern = r'(?<!h)ttps?://'

        # Replace incorrect 'ttp://' with 'http://' and 'ttps://' with 'https://'
        corrected_text = re.sub(pattern, lambda match: 'https://' if match.group(0).startswith('ttps') else 'http://', text)

        return corrected_text
    
    def remove_unknown(self, text, bot_id, bot_version, input_prompt):
        '''Removes the sentences that include the URLs that do not exist and are not in the database or the prompt of the bot'''
        # TODO:
        # 1. Currently, we detect the URL only based on http or https, but there are more than that
        # 2. When the bot generate the pattern like [xxx](yyy), we need to check yyy since it will trigger the markdown format
        # 3. Check yyy, and if yyy is valid then check whether it start from http, if so, add sentence, if not, add http://
        url_lists = []
        clean_text = ""

        # Define the headers to mimic a request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
        }
        
        connection = mysql_pool.get_connection()
        try:
            with connection.cursor() as cursor:
                document_sql = """
                SELECT URL FROM qa_doc_website WHERE qa_bot_id = %s AND qa_bot_version = %s
                """
                cursor.execute(document_sql, (bot_id, bot_version))
                results = cursor.fetchall()
                url_lists = [url[0] for url in results]
        finally:
            mysql_pool.close(connection)

        # This regex pattern splits text into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        for sentence in sentences:
            invalid = False
            if "http://" in sentence or "https://" in sentence:
                # Regular expression pattern to extract URLs
                url_pattern = r'https?://[\w.-]+(?:/[\w./?%&=-]*)?\b'

                # Find all occurrences of the pattern
                urls = re.findall(url_pattern, sentence)
                for url in urls:
                    if url not in url_lists and url not in input_prompt.text:
                        # Send the GET request
                        try:
                            response = requests.get(url, headers=headers)
                            if response.status_code != 200:
                                invalid = True
                                break
                        except Exception as e:
                            logger.info(f"Invalid link in generated response: {e}")
                            invalid = True
                            break

            if not invalid:
                clean_text += sentence + " "
        clean_text = clean_text.replace("()", "").replace("[]", "")
        
        return clean_text
    
    def remove_bracketed_pattern(self, text):
        '''
        Remove the sentences that contain bracketed patterns only, like [xxx].
        '''
        
        # Pattern explanation:
        # \[ : matches the character '['
        # .*? : matches any character (.) any number of times (*), as few times as possible to make the match succeed (?)
        # \] : matches the character ']'
        # \(# : matches the string '(#'
        # .*? : matches any character (.) any number of times (*), as few times as possible to make the match succeed (?)
        # \) : matches the character ')'
        pattern = re.compile(r'\[.*?\]\(\#.*?\)')
        # Replace the pattern with an empty string
        text = re.sub(pattern, '', text)

        # This regex pattern splits text into sentences
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        # This regex pattern checks if a sentence contains "[xxx]" not followed directly by "(http://"
        pattern = re.compile(r'\[.*?\](?!\(http)')
        # Rebuild the text excluding sentences that match the pattern
        filtered_text = ' '.join([sentence for sentence in sentences if not pattern.search(sentence)])

        return filtered_text
    
    def _process_url(self, ori_answer, bot_id, bot_version, input_prompt, **kwargs):
        # TODO: Each bot customize their own function

        cleaned_answer = ori_answer.strip()
        replace_targets = kwargs.get("process_url",[])
        for pairs in replace_targets:
            cleaned_answer = cleaned_answer.replace(pairs[0],pairs[1])

        # remove invalid url
        cleaned_answer = self.clean_error_url(cleaned_answer)
        cleaned_answer = self.remove_unknown(cleaned_answer, bot_id, bot_version, input_prompt)
        cleaned_answer = self.remove_bracketed_pattern(cleaned_answer)
        
        # For RichTech
        
        cleaned_answer	= cleaned_answer.replace(' https://richtech.bamboohr.com/careers', ' [https://richtech.bamboohr.com/careers](https://richtech.bamboohr.com/careers) ')
        cleaned_answer = cleaned_answer.replace(' https://ir.richtechrobotics.com/shareholder-services/email-alerts', ' [longer]')
        cleaned_answer = cleaned_answer.replace(' https://ir.richtechrobotics.com', ' [shorter]')
        cleaned_answer = cleaned_answer.replace(' [shorter]', ' [https://ir.richtechrobotics.com](https://ir.richtechrobotics.com) ')
        cleaned_answer = cleaned_answer.replace(' [longer]', ' [here](https://ir.richtechrobotics.com/shareholder-services/email-alerts) ')
        cleaned_answer = cleaned_answer.replace(' https://app.apollo.io/#/meet/up6-ohe-3g7/30-min', ' [https://app.apollo.io/#/meet/up6-ohe-3g7/30-min](https://app.apollo.io/#/meet/up6-ohe-3g7/30-min) ')

        # For Articulate AI
        cleaned_answer	= cleaned_answer.replace(' https://www.richtechrobotics.com/', ' [https://www.richtechrobotics.com](https://www.richtechrobotics.com) ')
        cleaned_answer = cleaned_answer.replace(' https://shorturl.at/crFLP', ' [https://shorturl.at/crFLP](https://shorturl.at/crFLP) ')

        return cleaned_answer
    
    def answer_guardrail(self, raw_gen_output, bot_id, bot_version, input_prompt, **kwargs):
        logger.info('raw answer: ' + raw_gen_output)
        if raw_gen_output.startswith('Assistant:'):
            raw_gen_output = raw_gen_output[len('Assistant:'):].strip()
        if raw_gen_output.startswith('ASSISTANT:'):
            raw_gen_output = raw_gen_output[len('ASSISTANT:'):].strip()
        cleaned_ans = self._process_url(raw_gen_output, bot_id, bot_version, input_prompt, **kwargs)
        logger.info('final answer: ' + cleaned_ans)

        return cleaned_ans

    
    def _prepare_output(self, result, params, product_kwargs):

        output = {
            "answer": result,
            "parameters": params,
            "has_follow_up": True,
        }

        return output