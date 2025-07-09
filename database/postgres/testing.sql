select id,
filename,
message_type,
status,
transcript_word_count
from data.audio_message
order by id asc;

delete from data.audio_message
where id in (78,79);

update data.audio_message
set status = 'archive';

update data.audio_message
set status = 'categorized'
where id = 75;
